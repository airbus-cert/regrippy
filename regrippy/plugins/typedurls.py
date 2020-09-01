from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Extracts URLs typed into Internet Explorer"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(r"Software\Microsoft\Internet Explorer\TypedURLs")
        if not key:
            return

        self.info(self.guess_username())
        for v in key.values():
            res = PluginResult(key=key, value=v)
            yield res

    def display_human(self, result):
        print(result.value_data)

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()}\t{result.value_data}", mtime=result.mtime
            )
        )
