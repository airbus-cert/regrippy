#!/usr/bin/env python
# ShimCacheParser.py
#
# Andrew Davis, andrew.davis@mandiant.com
# Copyright 2012 Mandiant
#
# Mandiant licenses this file to you under the Apache License, Version
# 2.0 (the "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# Identifies and parses Application Compatibility Shim Cache entries for forensic data.

import struct
import datetime
import codecs
from io import BytesIO
from csv import writer
import logging

logging.basicConfig()
logger = logging.getLogger("shimcacheparser")
logger.setLevel("ERROR")

# Values used by Windows 5.2 and 6.0 (Server 2003 through Vista/Server 2008)
CACHE_MAGIC_NT5_2 = 0xBADC0FFE
CACHE_HEADER_SIZE_NT5_2 = 0x8
NT5_2_ENTRY_SIZE32 = 0x18
NT5_2_ENTRY_SIZE64 = 0x20

# Values used by Windows 6.1 (Win7 and Server 2008 R2)
CACHE_MAGIC_NT6_1 = 0xBADC0FEE
CACHE_HEADER_SIZE_NT6_1 = 0x80
NT6_1_ENTRY_SIZE32 = 0x20
NT6_1_ENTRY_SIZE64 = 0x30
CSRSS_FLAG = 0x2

# Values used by Windows 5.1 (WinXP 32-bit)
WINXP_MAGIC32 = 0xDEADBEEF
WINXP_HEADER_SIZE32 = 0x190
WINXP_ENTRY_SIZE32 = 0x228
MAX_PATH = 520

# Values used by Windows 8
WIN8_STATS_SIZE = 0x80
WIN8_MAGIC = b"00ts"

# Magic value used by Windows 8.1
WIN81_MAGIC = b"10ts"

# Values used by Windows 10
WIN10_STATS_SIZE = 0x30
WIN10_CREATORS_STATS_SIZE = 0x34
WIN10_MAGIC = b"10ts"
CACHE_HEADER_SIZE_NT6_4 = 0x30
CACHE_MAGIC_NT6_4 = 0x30

bad_entry_data = "N/A"
g_verbose = False
g_usebom = False
output_header = ["Last Modified", "Last Update", "Path", "File Size", "Exec Flag"]

# Date Formats
DATE_MDY = "%m/%d/%y %H:%M:%S"
DATE_ISO = "%Y-%m-%d %H:%M:%S"
g_timeformat = DATE_ISO

# Shim Cache format used by Windows 5.2 and 6.0 (Server 2003 through Vista/Server 2008)
class CacheEntryNt5(object):
    def __init__(self, is32bit, data=None):

        self.is32bit = is32bit
        if data != None:
            self.update(data)

    def update(self, data):

        if self.is32bit:
            entry = struct.unpack("<2H 3L 2L", data)
        else:
            entry = struct.unpack("<2H 4x Q 2L 2L", data)
        self.wLength = entry[0]
        self.wMaximumLength = entry[1]
        self.Offset = entry[2]
        self.dwLowDateTime = entry[3]
        self.dwHighDateTime = entry[4]
        self.dwFileSizeLow = entry[5]
        self.dwFileSizeHigh = entry[6]

    def size(self):

        if self.is32bit:
            return NT5_2_ENTRY_SIZE32
        else:
            return NT5_2_ENTRY_SIZE64


# Shim Cache format used by Windows 6.1 (Win7 through Server 2008 R2)
class CacheEntryNt6(object):
    def __init__(self, is32bit, data=None):

        self.is32bit = is32bit
        if data != None:
            self.update(data)

    def update(self, data):

        if self.is32bit:
            entry = struct.unpack("<2H 7L", data)
        else:
            entry = struct.unpack("<2H 4x Q 4L 2Q", data)
        self.wLength = entry[0]
        self.wMaximumLength = entry[1]
        self.Offset = entry[2]
        self.dwLowDateTime = entry[3]
        self.dwHighDateTime = entry[4]
        self.FileFlags = entry[5]
        self.Flags = entry[6]
        self.BlobSize = entry[7]
        self.BlobOffset = entry[8]

    def size(self):

        if self.is32bit:
            return NT6_1_ENTRY_SIZE32
        else:
            return NT6_1_ENTRY_SIZE64


# Convert FILETIME to datetime.
# Based on http://code.activestate.com/recipes/511425-filetime-to-datetime/
def convert_filetime(dwLowDateTime, dwHighDateTime):

    try:
        date = datetime.datetime(1601, 1, 1, 0, 0, 0)
        temp_time = dwHighDateTime
        temp_time <<= 32
        temp_time |= dwLowDateTime
        return date + datetime.timedelta(microseconds=temp_time / 10)
    except OverflowError:
        return None


# Return a unique list while preserving ordering.
def unique_list(li):

    ret_list = []
    for entry in li:
        if entry not in ret_list:
            ret_list.append(entry)
    return ret_list


# Write the Log.
def write_it(rows, outfile=None):

    try:

        if not rows:
            logger.error("[-] No data to write...")
            return

        if not outfile:
            for row in rows:
                print(" ".join(["%s" % x for x in row]))
        else:
            logger.debug("[+] Writing output to %s..." % outfile)
            try:
                f = open(outfile, "wb")
                if g_usebom:
                    f.write(codecs.BOM_UTF8)
                csv_writer = writer(f, delimiter=",")
                csv_writer.writerows(rows)
                f.close()
            except IOError as err:
                logger.error("[-] Error writing output file: %s" % str(err))
                return

    except UnicodeEncodeError as err:
        logger.error("[-] Error writing output file: %s" % str(err))
        return


# Read the Shim Cache format, return a list of last modified dates/paths.
def read_cache(cachebin):

    if len(cachebin) < 16:
        # Data size less than minimum header size.
        return None

    try:
        # Get the format type
        magic = struct.unpack("<L", cachebin[0:4])[0]

        # This is a Windows 2k3/Vista/2k8 Shim Cache format,
        if magic == CACHE_MAGIC_NT5_2:

            # Shim Cache types can come in 32-bit or 64-bit formats. We can
            # determine this because 64-bit entries are serialized with u_int64
            # pointers. This means that in a 64-bit entry, valid UNICODE_STRING
            # sizes are followed by a NULL DWORD. Check for this here.
            test_size = struct.unpack("<H", cachebin[8:10])[0]
            test_max_size = struct.unpack("<H", cachebin[10:12])[0]
            if (
                test_max_size - test_size == 2
                and struct.unpack("<L", cachebin[12:16])[0]
            ) == 0:
                logger.debug("[+] Found 64bit Windows 2k3/Vista/2k8 Shim Cache data...")
                entry = CacheEntryNt5(False)
                return read_nt5_entries(cachebin, entry)

            # Otherwise it's 32-bit data.
            else:
                logger.debug("[+] Found 32bit Windows 2k3/Vista/2k8 Shim Cache data...")
                entry = CacheEntryNt5(True)
                return read_nt5_entries(cachebin, entry)

        # This is a Windows 7/2k8-R2 Shim Cache.
        elif magic == CACHE_MAGIC_NT6_1:
            test_size = struct.unpack(
                "<H", cachebin[CACHE_HEADER_SIZE_NT6_1 : CACHE_HEADER_SIZE_NT6_1 + 2]
            )[0]
            test_max_size = struct.unpack(
                "<H",
                cachebin[CACHE_HEADER_SIZE_NT6_1 + 2 : CACHE_HEADER_SIZE_NT6_1 + 4],
            )[0]

            # Shim Cache types can come in 32-bit or 64-bit formats.
            # We can determine this because 64-bit entries are serialized with
            # u_int64 pointers. This means that in a 64-bit entry, valid
            # UNICODE_STRING sizes are followed by a NULL DWORD. Check for this here.
            if (
                test_max_size - test_size == 2
                and struct.unpack(
                    "<L",
                    cachebin[CACHE_HEADER_SIZE_NT6_1 + 4 : CACHE_HEADER_SIZE_NT6_1 + 8],
                )[0]
            ) == 0:
                logger.debug("[+] Found 64bit Windows 7/2k8-R2 Shim Cache data...")
                entry = CacheEntryNt6(False)
                return read_nt6_entries(cachebin, entry)
            else:
                logger.debug("[+] Found 32bit Windows 7/2k8-R2 Shim Cache data...")
                entry = CacheEntryNt6(True)
                return read_nt6_entries(cachebin, entry)

        # This is WinXP cache data
        elif magic == WINXP_MAGIC32:
            logger.debug("[+] Found 32bit Windows XP Shim Cache data...")
            return read_winxp_entries(cachebin)

        # Check the data set to see if it matches the Windows 8 format.
        elif (
            len(cachebin) > WIN8_STATS_SIZE
            and cachebin[WIN8_STATS_SIZE : WIN8_STATS_SIZE + 4] == WIN8_MAGIC
        ):
            logger.debug("[+] Found Windows 8/2k12 Apphelp Cache data...")
            return read_win8_entries(cachebin, WIN8_MAGIC)

        # Windows 8.1 will use a different magic dword, check for it
        elif (
            len(cachebin) > WIN8_STATS_SIZE
            and cachebin[WIN8_STATS_SIZE : WIN8_STATS_SIZE + 4] == WIN81_MAGIC
        ):
            logger.debug("[+] Found Windows 8.1 Apphelp Cache data...")
            return read_win8_entries(cachebin, WIN81_MAGIC)

        # Windows 10 will use a different magic dword, check for it
        elif (
            len(cachebin) > WIN10_STATS_SIZE
            and cachebin[WIN10_STATS_SIZE : WIN10_STATS_SIZE + 4] == WIN10_MAGIC
        ):
            logger.debug("[+] Found Windows 10 Apphelp Cache data...")
            return read_win10_entries(cachebin, WIN10_MAGIC)

        # Windows 10 Creators Update will use a different STATS_SIZE, account for it
        elif (
            len(cachebin) > WIN10_CREATORS_STATS_SIZE
            and cachebin[WIN10_CREATORS_STATS_SIZE : WIN10_CREATORS_STATS_SIZE + 4]
            == WIN10_MAGIC
        ):
            logger.debug("[+] Found Windows 10 Creators Update Apphelp Cache data...")
            return read_win10_entries(cachebin, WIN10_MAGIC, creators_update=True)

        else:
            logger.error(
                "[-] Got an unrecognized magic value of 0x%x... bailing" % magic
            )
            return None

    except (RuntimeError, TypeError, NameError) as err:
        logger.error("[-] Error reading Shim Cache data: %s" % err)
        return None


# Read Windows 8/2k12/8.1 Apphelp Cache entry formats.
def read_win8_entries(bin_data, ver_magic):
    offset = 0
    entry_meta_len = 12
    entry_list = []

    # Skip past the stats in the header
    cache_data = bin_data[WIN8_STATS_SIZE:]

    data = BytesIO(cache_data)
    while data.tell() < len(cache_data):
        header = data.read(entry_meta_len)
        # Read in the entry metadata
        # Note: the crc32 hash is of the cache entry data
        magic, crc32_hash, entry_len = struct.unpack("<4sLL", header)

        # Check the magic tag
        if magic != ver_magic:
            raise Exception(
                "Invalid version magic tag found: 0x%x" % struct.unpack("<L", magic)[0]
            )

        entry_data = BytesIO(data.read(entry_len))

        # Read the path length
        path_len = struct.unpack("<H", entry_data.read(2))[0]
        if path_len == 0:
            path = "None"
        else:
            path = (
                entry_data.read(path_len).decode("utf-16le", "replace").encode("utf-8")
            )

        # Check for package data
        package_len = struct.unpack("<H", entry_data.read(2))[0]
        if package_len > 0:
            # Just skip past the package data if present (for now)
            entry_data.seek(package_len, 1)

        # Read the remaining entry data
        flags, unk_1, low_datetime, high_datetime, unk_2 = struct.unpack(
            "<LLLLL", entry_data.read(20)
        )

        # Check the flag set in CSRSS
        if flags & CSRSS_FLAG:
            exec_flag = "True"
        else:
            exec_flag = "False"

        last_mod_date = convert_filetime(low_datetime, high_datetime)
        try:
            last_mod_date = last_mod_date.strftime(g_timeformat)
        except ValueError:
            last_mod_date = bad_entry_data

        row = [last_mod_date, "N/A", path, "N/A", exec_flag]
        entry_list.append(row)

    return entry_list


# Read Windows 10 Apphelp Cache entry format
def read_win10_entries(bin_data, ver_magic, creators_update=False):

    offset = 0
    entry_meta_len = 12
    entry_list = []

    # Skip past the stats in the header
    if creators_update:
        cache_data = bin_data[WIN10_CREATORS_STATS_SIZE:]
    else:
        cache_data = bin_data[WIN10_STATS_SIZE:]

    data = BytesIO(cache_data)
    while data.tell() < len(cache_data):
        header = data.read(entry_meta_len)
        # Read in the entry metadata
        # Note: the crc32 hash is of the cache entry data
        magic, crc32_hash, entry_len = struct.unpack("<4sLL", header)

        # Check the magic tag
        if magic != ver_magic:
            raise Exception(
                "Invalid version magic tag found: 0x%x" % struct.unpack("<L", magic)[0]
            )

        entry_data = BytesIO(data.read(entry_len))

        # Read the path length
        path_len = struct.unpack("<H", entry_data.read(2))[0]
        if path_len == 0:
            path = "None"
        else:
            path = entry_data.read(path_len).decode("utf-16le", "replace")

        # Read the remaining entry data
        low_datetime, high_datetime = struct.unpack("<LL", entry_data.read(8))

        last_mod_date = convert_filetime(low_datetime, high_datetime)
        try:
            last_mod_date = last_mod_date.strftime(g_timeformat)
        except ValueError:
            last_mod_date = bad_entry_data

        # Skip the unrecognized Microsoft App entry format for now
        if last_mod_date == bad_entry_data:
            continue

        row = [last_mod_date, "N/A", path, "N/A", "N/A"]
        entry_list.append(row)

    return entry_list


# Read Windows 2k3/Vista/2k8 Shim Cache entry formats.
def read_nt5_entries(bin_data, entry):

    try:
        entry_list = []
        contains_file_size = False
        entry_size = entry.size()
        exec_flag = ""

        num_entries = struct.unpack("<L", bin_data[4:8])[0]
        if num_entries == 0:
            return None

        # On Windows Server 2008/Vista, the filesize is swapped out of this
        # structure with two 4-byte flags. Check to see if any of the values in
        # "dwFileSizeLow" are larger than 2-bits. This indicates the entry contained file sizes.
        for offset in range(
            CACHE_HEADER_SIZE_NT5_2,
            (num_entries * entry_size) + CACHE_HEADER_SIZE_NT5_2,
            entry_size,
        ):

            entry.update(bin_data[offset : offset + entry_size])

            if entry.dwFileSizeLow > 3:
                contains_file_size = True
                break

        # Now grab all the data in the value.
        for offset in range(
            CACHE_HEADER_SIZE_NT5_2,
            (num_entries * entry_size) + CACHE_HEADER_SIZE_NT5_2,
            entry_size,
        ):

            entry.update(bin_data[offset : offset + entry_size])

            last_mod_date = convert_filetime(entry.dwLowDateTime, entry.dwHighDateTime)
            try:
                last_mod_date = last_mod_date.strftime(g_timeformat)
            except ValueError:
                last_mod_date = bad_entry_data
            path = bin_data[entry.Offset : entry.Offset + entry.wLength].decode(
                "utf-16le", "replace"
            )

            # It contains file size data.
            if contains_file_size:
                hit = [last_mod_date, "N/A", path, str(entry.dwFileSizeLow), "N/A"]
                if hit not in entry_list:
                    entry_list.append(hit)

            # It contains flags.
            else:
                # Check the flag set in CSRSS
                if entry.dwFileSizeLow & CSRSS_FLAG:
                    exec_flag = "True"
                else:
                    exec_flag = "False"

                hit = [last_mod_date, "N/A", path, "N/A", exec_flag]
                if hit not in entry_list:
                    entry_list.append(hit)

        return entry_list

    except (RuntimeError, ValueError, NameError) as err:
        logger.error("[-] Error reading Shim Cache data: %s..." % err)
        return None


# Read the Shim Cache Windows 7/2k8-R2 entry format,
# return a list of last modifed dates/paths.
def read_nt6_entries(bin_data, entry):

    try:
        entry_list = []
        exec_flag = ""
        entry_size = entry.size()
        num_entries = struct.unpack("<L", bin_data[4:8])[0]

        if num_entries == 0:
            return None

        # Walk each entry in the data structure.
        for offset in range(
            CACHE_HEADER_SIZE_NT6_1,
            num_entries * entry_size + CACHE_HEADER_SIZE_NT6_1,
            entry_size,
        ):

            entry.update(bin_data[offset : offset + entry_size])
            last_mod_date = convert_filetime(entry.dwLowDateTime, entry.dwHighDateTime)
            try:
                last_mod_date = last_mod_date.strftime(g_timeformat)
            except ValueError:
                last_mod_date = "N/A"
            path = bin_data[entry.Offset : entry.Offset + entry.wLength].decode(
                "utf-16le", "replace"
            )

            # Test to see if the file may have been executed.
            if entry.FileFlags & CSRSS_FLAG:
                exec_flag = "True"
            else:
                exec_flag = "False"

            hit = [last_mod_date, "N/A", path, "N/A", exec_flag]

            if hit not in entry_list:
                entry_list.append(hit)
        return entry_list

    except (RuntimeError, ValueError, NameError) as err:
        logger.error("[-] Error reading Shim Cache data: %s..." % err)
        return None


# Read the WinXP Shim Cache data. Some entries can be missing data but still
# contain useful information, so try to get as much as we can.
def read_winxp_entries(bin_data):

    entry_list = []

    try:

        num_entries = struct.unpack("<L", bin_data[8:12])[0]
        if num_entries == 0:
            return None

        for offset in range(
            WINXP_HEADER_SIZE32,
            (num_entries * WINXP_ENTRY_SIZE32) + WINXP_HEADER_SIZE32,
            WINXP_ENTRY_SIZE32,
        ):

            # No size values are included in these entries, so search for utf-16 terminator.
            path_len = bin_data[offset : offset + (MAX_PATH + 8)].find("\x00\x00")

            # if path is corrupt, procede to next entry.
            if path_len == 0:
                continue
            path = bin_data[offset : offset + path_len + 1].decode("utf-16le")

            entry_data = offset + (MAX_PATH + 8)

            # Get last mod time.
            last_mod_time = struct.unpack("<2L", bin_data[entry_data : entry_data + 8])
            try:
                last_mod_time = convert_filetime(
                    last_mod_time[0], last_mod_time[1]
                ).strftime(g_timeformat)
            except ValueError:
                last_mod_time = "N/A"

            # Get last file size.
            file_size = struct.unpack(
                "<2L", bin_data[entry_data + 8 : entry_data + 16]
            )[0]
            if file_size == 0:
                file_size = bad_entry_data

            # Get last update time.
            exec_time = struct.unpack(
                "<2L", bin_data[entry_data + 16 : entry_data + 24]
            )
            try:
                exec_time = convert_filetime(exec_time[0], exec_time[1]).strftime(
                    g_timeformat
                )
            except ValueError:
                exec_time = bad_entry_data

            hit = [last_mod_time, exec_time, path, file_size, "N/A"]
            if hit not in entry_list:
                entry_list.append(hit)
        return entry_list

    except (RuntimeError, ValueError, NameError) as err:
        logger.error("[-] Error reading Shim Cache data %s" % err)
        return None
