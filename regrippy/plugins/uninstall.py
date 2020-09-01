from regrippy import BasePlugin, PluginResult, mactime
from Registry import Registry


class Plugin(BasePlugin):
    """Lists installed software"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        key = self.open_key("Microsoft\\Windows\\CurrentVersion\\Uninstall")
        if not key:
            return

        for program in key.subkeys():
            try:
                display_name = program.value("DisplayName").value()
            except Registry.RegistryValueNotFoundException:
                display_name = "[N/A]"

            try:
                uninstall_string = program.value("UninstallString").value()
            except Registry.RegistryValueNotFoundException:
                uninstall_string = "[N/A]"

            res = PluginResult(key=program)
            res.custom["display_name"] = display_name
            res.custom["uninstall_string"] = uninstall_string
            yield res

    def display_human(self, result):
        print(
            f"{result.key_name} ({result.custom['display_name']})\n\t{result.custom['uninstall_string']}\n"
        )

    def display_machine(self, result):
        print(
            mactime(
                name=f"{result.key_name};{result.custom['display_name']};{result.custom['uninstall_string']}",
                mtime=result.mtime,
            )
        )
