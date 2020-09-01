import struct

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Extract local group information from the SAM & SOFTWARE databases"""

    # In this case, order matters. The plugins needs the SOFTWARE hive to be parsed first to preperly enrich results.
    __REGHIVE__ = ["SOFTWARE", "SAM"]

    # Use class variable to persist across runs
    user_profile_list = []

    def sid2asc(self, bin_sid):
        """Turns a binary SID into its ASCII representation"""
        # SID structure:
        #   + 1 byte (revision, little endian)
        #   + 1 byte (count of sub auths, little endian)
        #   + 6 bytes (authority value, big endian)
        #   + n * 4 bytes where n is the count of sub auths

        # Construct the fixed-length part of the SID
        rev, sub_auth_count, bytes_idauth = struct.unpack("<BB6s", bin_sid[:8])
        int_idauth = int.from_bytes(bytes_idauth, byteorder="big", signed=False)
        str_sid = "S-{0}-{1}".format(rev, int_idauth)

        # Get the variable part and iterate over each sub auth (4-byte little-endian integer)
        bin_sub_auths = bin_sid[8:]
        for i in range(0, sub_auth_count * 4, 4):
            str_sid += "-{0}".format(struct.unpack("<L", bin_sub_auths[i : i + 4])[0])

        return str_sid

    def machine_sid(self):
        """Gets the machine SID from the SAM hive"""
        # The machine SID on which all local accounts are based sits at the end of the Account key's V data
        key_machine = self.open_key("SAM\\Domains\\Account")
        v_raw = key_machine.value("V").value()
        v_data = v_raw[len(v_raw) - 24 :]
        return self.sid2asc(v_data)

    def user_sids_sam(self):
        """Gets user SIDs from the SAM hive"""
        machine_sid = self.machine_sid()
        key_accounts = self.open_key("SAM\\Domains\\Account\\Users\\Names")
        if not key_accounts:
            return
        for subkey in key_accounts.subkeys():
            # User SIDs are built by appending their Relative ID to the machine SID.
            # Relative IDs are stored inside Names' subkeys; each has a default value where the value *type* holds the
            # integer value of the RID.
            sid = "{0}-{1}".format(machine_sid, subkey.value("(default)").value_type())
            # User names are stored inside Names' subkeys; each subkey's name holds the associated user name.
            name = subkey.name()
            if not any(
                profile.get("sid", None) == sid for profile in self.user_profile_list
            ):
                self.user_profile_list.append({"sid": sid, "name": name})
        return

    def user_sids_soft(self):
        """Gets user SIDs from the SOFTWARE hive"""
        key_profiles = self.open_key(
            "Microsoft\\Windows NT\\CurrentVersion\\ProfileList"
        )
        if not key_profiles:
            return
        for subkey in key_profiles.subkeys():
            # User SIDs are stored inside ProfileList's subkeys; each subkey's name holds the associated user SID.
            sid = subkey.name()
            # The "profile path" points to the user folder; we can use it to map the SID to the user
            name = subkey.value("ProfileImagePath").value().rpartition("\\")[2]
            if not any(
                profile.get("sid", None) == sid for profile in self.user_profile_list
            ):
                self.user_profile_list.append({"sid": sid, "name": name})
        return

    def yield_groups(self):
        """Yields a dictionary representation of groups and their members, from the SAM hive"""
        key_groups = self.open_key("SAM\\Domains\\Builtin\\Aliases")
        if not key_groups:
            return

        # Yield a custom structure with information from the SAM hive
        for subkey in key_groups.subkeys():
            if subkey.name().startswith("00000"):
                c_raw = subkey.value("C").value()
                # Header is 13 little-endian unsigned long values and holds among others:
                # - Group's name offset and length
                # - Group's description offset and length
                # - Group members' offset and size (as binary SIDs)
                c_header = struct.unpack("<13L", c_raw[:0x34])
                c_data = c_raw[0x34:]
                c_gname_off = c_header[4]
                c_gname_len = c_header[5]
                c_gdesc_off = c_header[7]
                c_gdesc_len = c_header[8]
                c_gmembers_off = c_header[10]
                c_gmembers_size = c_header[12]

                member_sid_list = []
                off = c_gmembers_off
                for _ in range(c_gmembers_size):
                    # 1 member == 1 binary SID
                    # SID structure:
                    #   + 1 byte (revision, little endian)
                    #   + 1 byte (count of sub auths, little endian)
                    #   + 6 bytes (authority value, big endian)
                    #   + n * 4 bytes where n is the count of sub auths
                    # Look ahead to check the count of sub authorities to compute SID size
                    sub_auth_count = struct.unpack("<B", c_data[off + 1 : off + 2])[0]
                    sid_size = 8 + sub_auth_count * 4
                    member_sid_list.append(self.sid2asc(c_data[off : off + sid_size]))
                    off += sid_size

                res = PluginResult(key=subkey, value=None)
                res.custom = {
                    "name": c_data[c_gname_off : c_gname_off + c_gname_len].decode(
                        "utf-16-le"
                    ),
                    "desc": c_data[c_gdesc_off : c_gdesc_off + c_gdesc_len].decode(
                        "utf-16-le"
                    ),
                    "size": c_gmembers_size,
                    "member_sids": member_sid_list,
                }
                yield res

    def run(self):
        if self.hive_name == "SOFTWARE":
            self.user_sids_soft()
        elif self.hive_name == "SAM":
            self.user_sids_sam()
            yield from self.yield_groups()

    def display_human(self, res):
        group = res.custom
        print('"{0}" with {1} direct members'.format(group["name"], group["size"]))
        if group["size"] > 0:
            for member_sid in group["member_sids"]:
                mapped_user = ""
                for user in self.user_profile_list:
                    if user["sid"] == member_sid:
                        mapped_user = user["name"]
                if mapped_user != "":
                    print("\t{0} ({1})".format(member_sid, mapped_user))
                else:
                    print("\t{0}".format(member_sid))

    def display_machine(self, res):
        print(mactime(name=res.custom["name"], mtime=res.mtime))
