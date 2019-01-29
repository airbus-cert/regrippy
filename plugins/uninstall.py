from Registry import Registry

__REGHIVE__ = "SOFTWARE"
__DESCRIPTION__ = "Lists installed software"

def run(reg, pipe, logger):
    try:
        key = reg.open(r"Microsoft\Windows\CurrentVersion\Uninstall")

        for subkey in key.subkeys():
            t = subkey.timestamp()

            display_name = [v.value() for v in subkey.values() if v.name() == "DisplayName"]
            if not display_name:
                display_name = "[N/A]"
            else:
                display_name = display_name[0]
            
            uninstall = [v.value() for v in subkey.values() if v.name() == "UninstallString"]
            if not uninstall:
                uninstall = "[N/A]"
            else:
                uninstall = uninstall[0]
            
            if pipe:
                print(mactime(name=display_name, mtime=int(t.timestamp())))
            else:
                print(display_name, "-", t, "\n\t", uninstall, "\n")
    except Registry.RegistryKeyNotFoundException:
        logger.warning("Microsoft\\Windows\\CurrentVersion\\Uninstall not found")
