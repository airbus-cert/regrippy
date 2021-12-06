from datetime import datetime

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Reads TeamViewer configuration"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        path = r"TeamViewer"

        k = self.open_key(path)
        if not k:
            return

        r = PluginResult(key=k)

        r.custom = {
            "AlwaysOnline": k.value("Always_Online").value() == 1,
            "ClientID": k.value("ClientID").value(),
            "LastStartupTime": k.value("LastStartupTime"),
        }
        yield r

    def display_human(self, r):
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
