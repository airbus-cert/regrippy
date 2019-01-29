from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Extracts URLs typed into Internet Explorer"

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Internet Explorer\TypedURLs")

        for v in key.values():
            print(v.value())
    except Registry.RegistryKeyNotFoundException:
        logger.warning("Software\\Microsoft\\Internet Explorer\\TypedURLs not found")