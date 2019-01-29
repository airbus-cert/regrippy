from Registry import Registry

__REGHIVE__ = "NTUSER.DAT"
__DESCRIPTION__ = "Reads OpenSaveMRU and LastVisitedMRU keys (Most Recently Used files in Save As / Open file dialogs)"

def run(reg, pipe, logger):
    for path in [r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedMRU"]:
        try:
            key = reg.open(path)
            if not key.values():
                return

            order = [v for v in key.values() if v.name() == "MRUList"]
            values = dict([(v.name(), v.value()) for v in key.values() if v.name() != "MRUList"])

            for letter in order[0].value():
                print(values[letter])
        except Registry.RegistryKeyNotFoundException:
            logger.warning(f"{path} does not exist")