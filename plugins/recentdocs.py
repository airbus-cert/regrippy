from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Lists 'My Recent Documents'"

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs")

        for v in key.values():
            if v.name() == "MRUListEx":
                continue

            binary = v.value()
            offset_str_end = binary.find(b"\x00\x00")
            docname = binary[:offset_str_end+1].decode("utf16")

            if pipe:
                print(mactime(name=docname, mtime=int(key.timestamp().timestamp())))

    except Registry.RegistryKeyNotFoundException:
        logger.warning("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs not found")
