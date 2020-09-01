from regrippy import BasePlugin, PluginResult, mactime

# The entries in "ConvertUserDevModesCount" are not removed when a printer is deleted


class Plugin(BasePlugin):
    """Lists all printers that were connected to this machine"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        k = self.open_key(r"Printers\ConvertUserDevModesCount")
        if not k:
            return

        for v in k.values():
            r = PluginResult(key=k, value=v)
            yield r

    def display_human(self, result):
        print(result.value_name)

    def display_machine(self, result):
        print(mactime(name=result.value_name, mtime=result.mtime))
