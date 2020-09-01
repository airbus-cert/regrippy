from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads OpenSaveMRU and LastVisitedMRU keys (Most Recently Used files in Save As / Open file dialogs)"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        for path in [
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU",
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedMRU",
        ]:
            key = self.open_key(path)
            if not key or not key.values():
                continue

            order = key.value("MRUList").value()
            values = dict(
                [(v.name(), v) for v in key.values() if v.name() != "MRUList"]
            )

            for letter in order:
                yield PluginResult(key=key, value=values[letter])

    def display_human(self, result):
        print(result.value_data)

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()}\t{result.value_data}", mtime=result.mtime
            )
        )
