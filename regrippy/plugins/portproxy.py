from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Lists all network redirections configured on the system"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        ccs = self.get_currentcontrolset_path()
        if not ccs:
            return

        for proto in ["tcp", "udp"]:
            key = self.open_key(ccs + "\\Services\\PortProxy\\v4tov4\\" + proto)
            if not key:
                continue

            for value in key.values():
                res = PluginResult(key=key, value=value)
                res.custom["proto"] = proto
                yield res

    def display_human(self, result):
        print(f"{result.custom['proto']} - {result.value_name} => {result.value_data}")

    def display_mactime(self, result):
        print(
            mactime(
                name=f"{result.custom['proto']} {result.value_name} {result.value_data}",
                mtime=result.mtime,
            )
        )
