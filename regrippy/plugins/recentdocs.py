from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Lists 'My Recent Documents'"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
        )
        if not key:
            return

        for v in key.values():
            if v.name() == "MRUListEx":
                continue

            binary = v.value()
            offset_str_end = binary.find(b"\x00\x00")
            docname = binary[: offset_str_end + 1].decode("utf16")

            res = PluginResult(key=key, value=v)
            res.custom["docname"] = docname
            yield res

    def display_human(self, result):
        print(result.custom["docname"])

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()}\t{result.custom['docname']}",
                mtime=result.mtime,
            )
        )
