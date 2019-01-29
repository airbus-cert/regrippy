from Registry import Registry

__REGHIVE__ = "SYSTEM"
__DESCRIPTION__ = "Lists all services installed on the system"

def run(reg, pipe, logger):
    controlset_keys = [k for k in reg.root().subkeys() if k.name().startswith("ControlSet")]

    for cskey in controlset_keys:
        key = reg.open(cskey.name() + r"\Services")

        for service in key.subkeys():
            print(service.name(), "-", service.timestamp())
            for value in service.values():
                if value.name() == "ImagePath":
                    print("\tImagePath =", value.value())
            print()
            