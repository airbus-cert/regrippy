from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Gets the name of the last logged-on user"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        key = self.open_key(
            "Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI"
        )
        if not key:
            return

        for v in key.values():
            if (
                v.name().startswith("LastLoggedOn")
                and v.name() != "LastLoggedOnProvider"
            ):
                res = PluginResult(key=key, value=v)
                yield res

    def display_human(self, result):
        print(result.value_name, "\t", result.value_data)

    def display_machine(self, result):
        print(
            mactime(name=f"{result.value_name} {result.value_data}", mtime=result.mtime)
        )
