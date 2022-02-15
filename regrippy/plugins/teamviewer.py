from datetime import datetime

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads TeamViewer configuration"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        path = r"TeamViewer"

        k = self.open_key(path)
        if k:
            yield from self.process_key(k)

        k = self.open_key("Wow6432Node\\" + path)
        if k:
            yield from self.process_key(k)

    def process_key(self, k):
        r = PluginResult(key=k)

        values = [x.name() for x in k.values()]

        r.custom = {
            "AlwaysOnline": k.value("Always_Online").value() == 1,
            "ClientID": k.value("ClientID").value(),
            "LastStartupTime": k.value("LastStartupTime")
            if "LastStartupTime" in values
            else -1,
            "Version": k.value("Version").value(),
        }
        yield r

    def display_human(self, r):
        if "wow6432node" in r.path.lower():
            print("[32-bit application]")

        print(f"Always Online: {r.custom['AlwaysOnline']}")
        print(f"Client ID: {r.custom['ClientID']}")
        print(
            f"LastStartupTime: {r.custom['LastStartupTime']} ({datetime.fromtimestamp(r.custom['LastStartupTime'])})"
        )

    def display_machine(self, r):
        print(
            mactime(
                mtime=r.custom["LastStartupTime"],
                name=f"TeamViewer startup ({r.custom['ClientID']})",
            )
        )
