from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Lists all printer ports setup on the machine"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        k = self.open_key(r"Microsoft\Windows NT\CurrentVersion\Ports")
        if not k:
            return

        for v in k.values():
            r = PluginResult(key=k, value=v)
            yield r

    def display_human(self, result):
        print(f"{result.value_name}: {result.value_data}")

    def display_machine(self, result):
        print(
            mactime(name=f"{result.value_name},{result.value_data}", mtime=result.mtime)
        )
