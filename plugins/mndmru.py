from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Reads 'Map Network Drive MRU' key (Most Recently Used remote drives)"

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Map Network Drive MRU")
        if not key.values():
            return

        order = [v for v in key.values() if v.name() == "MRUList"]
        values = dict([(v.name(), v.value()) for v in key.values() if v.name() != "MRUList"])

        for letter in order[0].value():
            print(values[letter])
    except Registry.RegistryKeyNotFoundException:
        logger.warning("MapNetworkDriveMRU does not exist")