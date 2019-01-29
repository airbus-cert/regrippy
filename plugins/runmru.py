from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Reads RunMRU key (Most Recently Used programs)"

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU")
        if not key.values():
            return

        order = [v for v in key.values() if v.name() == "MRUList"]
        values = dict([(v.name(), v.value()) for v in key.values() if v.name() != "MRUList"])

        for letter in order[0].value():
            print(values[letter])
    except Registry.RegistryKeyNotFoundException:
        logger.warning("RunMRU does not exist")