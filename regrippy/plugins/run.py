from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads startup programs from various hives"""

    __REGHIVE__ = ["NTUSER.DAT", "SOFTWARE"]

    def run(self):
        if self.hive_name == "NTUSER.DAT":
            paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
                r"Software\Microsoft\Windows NT\CurrentVersion\Windows\Run",
            ]
        else:  # SOFTWARE
            paths = [
                r"Microsoft\Windows\CurrentVersion\Run",
                r"Microsoft\Windows\CurrentVersion\RunOnce",
                r"Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
            ]

        for path in paths:
            key = self.open_key(path)
            if not key:
                continue

            for v in key.values():
                res = PluginResult(key=key, value=v)
                yield res

    def display_human(self, result):
        print(result.value_name, "//", result.value_data)

    def display_machine(self, result):
        print(
            mactime(
                name=f"{result.value_name}\t{result.value_data}", mtime=result.mtime
            )
        )
