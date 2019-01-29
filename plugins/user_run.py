from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Reads startup programs from NTUSER.DAT"

def run(reg, pipe, logger):
    for path in [r"Software\Microsoft\Windows\CurrentVersion\Run", r"Software\Microsoft\Windows\CurrentVersion\RunOnce", 
    r"Software\Microsoft\Windows NT\CurrentVersion\Windows\Run"]:
        try:
            key = reg.open(path)

            t = key.timestamp()

            if not pipe:
                print(path)
                print("Last modified:", t)

            for value in key.values():
                if pipe:
                    print(mactime(name=value.name() +"\t" + value.value(), mtime=int(t.timestamp())))
                else:
                    print(f"\t{value.name()}: {value.value()}")
            print()
        except Registry.RegistryKeyNotFoundException:
            logger.warning(f"{path} not found")