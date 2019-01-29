import time

from Registry import Registry

__REGHIVE__ = "SOFTWARE"
__DESCRIPTION__ = "Reads startup programs from SOFTWARE"

def run(reg, pipe, logger):
    for path in [r"Microsoft\Windows\CurrentVersion\Run", r"Microsoft\Windows\CurrentVersion\RunOnce", r"Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"]:
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
        except Registry.RegistryKeyNotFoundException:
            logger.warning(f"{path} not found")