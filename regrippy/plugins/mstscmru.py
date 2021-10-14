from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads Terminal Client (aka mstsc.exe) Most Recently Used address"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(r"Software\Microsoft\Terminal Server Client\Default")
        if not key or not key.values():
            return

        for value in key.values():
            res = PluginResult(key=key, value=value)
            yield res

    def display_human(self, result):
        print(result.value_data)

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()}\t{result.value_data}", mtime=result.mtime
            )
        )
