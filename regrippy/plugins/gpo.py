from Registry.Registry import RegistryValueNotFoundException

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """list all GPOs applied on this system"""

    __REGHIVE__ = ["SOFTWARE", "NTUSER.DAT"]

    EXTENSIONS = {
        "{35378EAC-683F-11D2-A89A-00C04FBBCFA2}": "Registry Settings",
    }

    def run(self):
        path = r"Microsoft\Windows\CurrentVersion\Group Policy\History"
        if self.hive_name == "NTUSER.DAT":
            path = "SOFTWARE\\" + path
        else:
            self.get_gp_extensions()

        k = self.open_key(path)
        if not k:
            return

        for subkey in k.subkeys():
            for gpo in subkey.subkeys():
                r = PluginResult(key=gpo)
                r.custom = {
                    "Extension": self.EXTENSIONS.get(subkey.name(), subkey.name()),
                    "DisplayName": gpo.value("DisplayName").value(),
                    "DSPath": (
                        gpo.value("DSPath").value()
                        if "DSPath" in [x.name() for x in gpo.values()]
                        else "N/A"
                    ),
                    "Path": gpo.value("FileSysPath").value(),
                    "GPOName": gpo.value("GPOName").value(),
                    "IParam": (
                        gpo.value("IParam").value()
                        if "IParam" in [x.name() for x in gpo.values()]
                        else "N/A"
                    ),
                    "Options": (
                        gpo.value("Options").value()
                        if "Options" in [x.name() for x in gpo.values()]
                        else "N/A"
                    ),
                }
                yield r

    def get_gp_extensions(self):
        k = self.open_key(r"Microsoft\Windows NT\CurrentVersion\Winlogon\GPExtensions")
        if not k:
            return

        for subkey in k.subkeys():
            guid = subkey.name()
            if guid in self.EXTENSIONS.keys():
                continue

            name = guid
            try:
                name = subkey.value("(default)").value()
            except RegistryValueNotFoundException:
                pass
            self.EXTENSIONS[guid] = name

    def display_human(self, r):
        print(f"[{r.custom['Extension']}] {r.custom['DisplayName']}")
        print(f"\tPath: {r.custom['Path']}")
        print(f"\tDSPath: {r.custom['DSPath']}")
        print(f"\tGPOName: {r.custom['GPOName']}")
        print(f"\tIParam: {r.custom['IParam']}")
        print(f"\tOptions: {r.custom['Options']}")
        print()

    def display_machine(self, r):
        print(
            mactime(
                name=f"GPO: {r.custom['DisplayName']} [{r.custom['Extension']}] :: {r.custom['GPOName']}",
                mtime=r.mtime,
            )
        )
