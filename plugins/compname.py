from Registry import Registry

__REGHIVE__ = "SYSTEM"
__DESCRIPTION__ = "Returns the computer name"

def run(reg, pipe, logger):
    controlset_keys = [k for k in reg.root().subkeys() if k.name().startswith("ControlSet")]
    names = []

    for cskey in controlset_keys:
        key = reg.open(cskey.name() + r"\Control\ComputerName\ComputerName")

        names.append(key.value("ComputerName").value())

    dedup = []
    for n in names:
        if n not in dedup:
            dedup.append(n)
            print(n)
