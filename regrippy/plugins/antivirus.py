from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """gets the default antivirus, and retrieves the status of all installed antiviruses"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        k = self.open_key(r"Microsoft\Security Center\Provider\Av")
        if not k:
            return

        for subkey in k.subkeys():
            r = PluginResult(key=subkey)
            r.custom = {
                "DisplayName": subkey.value("DISPLAYNAME").value(),
                "ProductExe": subkey.value("PRODUCTEXE").value(),
                "ReportingExe": subkey.value("REPORTINGEXE").value(),
                "State": " | ".join(self.parse_state(subkey.value("STATE").value())),
            }
            yield r

    def display_human(self, r):
        print(f"{r.custom['DisplayName']}")
        print(f"\t{r.custom['ProductExe']}")
        print(f"\t{r.custom['State']}")
        print()

    def parse_state(self, state):
        # Source: https://mcpforlife.com/2020/04/14/how-to-resolve-this-state-value-of-av-providers/
        enums = []

        if state & 0x3000 == 0x3000:
            enums.append("EXPIRED")
        elif state & 0x2000 == 0x2000:
            enums.append("SNOOZED")
        elif state & 0x1000 == 0x1000:
            enums.append("ON")
        else:
            enums.append("OFF")

        if state & 0x10 == 0x10:
            enums.append("OUT_OF_DATE")
        else:
            enums.append("UP_TO_DATE")

        if state & 0x100 == 0x100:
            enums.append("MICROSOFT_PRODUCT")
        else:
            enums.append("NON_MICROSOFT_PRODUCT")

        return enums
