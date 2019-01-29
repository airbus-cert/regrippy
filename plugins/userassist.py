import codecs

from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Parses the UserAssist key to get information on program usage"

GUIDS = [
    # Windows XP
    "{75048700-EF1F-11D0-9888-006097DEACF9}",
    "{5E6AB780-7743-11CF-A12B-00AA004AE837}",

    # Windows 7+
    "{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}",
    "{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F}",
]

class UAObject(object):
    LENGTH_WINXP = 16
    LENGTH_WIN7 = 72

    def __init__(self, name, raw):
        self._raw = raw
        self.name = codecs.encode(name, "rot13") # TODO: translate using https://www.aldeid.com/wiki/Windows-userassist-keys#Translation_of_directories
        self.number_of_execs = self._read_nb_execs()
        self.focus_time_secs = self._read_focus_time()
        self.last_exec = self._read_last_exec()
    
    def _read_nb_execs(self):
        if len(self._raw) == UAObject.LENGTH_WINXP:
            return int.from_bytes(self._raw[4:8], byteorder="little") - 5
        else:
            return int.from_bytes(self._raw[4:8], byteorder="little")
        
    def _read_focus_time(self):
        if len(self._raw) == UAObject.LENGTH_WINXP:
            return 0
        
        return int.from_bytes(self._raw[12:16], byteorder="little")
    
    def _read_last_exec(self):
        timestamp = 0
        if len(self._raw) == UAObject.LENGTH_WINXP:
            timestamp = int.from_bytes(self._raw[8:16], byteorder="little")
        else:
            timestamp = int.from_bytes(self._raw[60:68], byteorder="little")
        
        no_nano = timestamp//10000000 # 10000000 - 100 nanosecond intervals in windows timestamp, remove them to get to seconds since windows epoch
        unix = no_nano - 11644473600 # number of seconds between 1/1/1601 and 1/1/1970

        return unix

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist")

        t = key.timestamp()
        
        # Each subkey is a GUID identifying a specific location
        for subkey in key.subkeys():
            if subkey.name() not in GUIDS:
                continue
            
            count_key = subkey.subkey("Count")
            if not count_key:
                continue

            for value in count_key.values():
                entry = UAObject(value.name(), value.value())

                print(f"{entry.name} - executed {entry.number_of_execs} times / focused {entry.focus_time_secs}s / last exec: {entry.last_exec}")
    except Registry.RegistryKeyNotFoundException:
        logger.warning("UserAssist not found")