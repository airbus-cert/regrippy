from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads RunMRU key (Most Recently Used programs)"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
        )
        if not key or not key.values():
            return

        order = key.value("MRUList")
        values = dict([(v.name(), v) for v in key.values() if v.name() != "MRUList"])

        for letter in order.value():
            res = PluginResult(key=key, value=values[letter])
            yield res

    def display_human(self, result):
        print(result.value_data)

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()}\t{result.value_data}", mtime=result.mtime
            )
        )
