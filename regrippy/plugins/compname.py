from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Returns the computer name"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(
            self.get_currentcontrolset_path() + "\\Control\\ComputerName\\ComputerName"
        )
        if not key:
            return

        compname = key.value("ComputerName")

        res = PluginResult(key=key, value=compname)
        yield res

    def display_human(self, result):
        print(result.value_data)

    def display_machine(self, result):
        print(mactime(name=result.value_data, mtime=result.mtime))
