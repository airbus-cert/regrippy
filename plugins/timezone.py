from Registry import Registry

__REGHIVE__ = "SYSTEM"
__DESCRIPTION__ = "Returns the computer's timezone"

def run(reg, pipe, logger):
    controlset_keys = [k for k in reg.root().subkeys() if k.name().startswith("ControlSet")]
    tz = []

    for cskey in controlset_keys:
        key = reg.open(cskey.name() + r"\Control\TimeZoneInformation")

        tz.append(key.value("TimeZoneKeyName").value())

    dedup = []
    for t in tz:
        if t not in dedup:
            dedup.append(t)
            print(t)
