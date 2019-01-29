from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Reads the contents of 'Protected Storage System Provider' (Never tested)"

def dump(key, depth=0):
    for value in key.values():
        print("\t" * depth, f"📕 [{value.name()}] {value.value()}")
    
    for subkey in key.subkeys():
        print("\t" * depth, f"📁 {subkey.name()}")
        dump(subkey, depth=depth+1)

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Protected Storage System Provider")
        
        dump(key)

    except Registry.RegistryKeyNotFoundException:
        logger.warning("RunMRU does not exist")