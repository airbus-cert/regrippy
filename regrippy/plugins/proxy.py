from regrippy import BasePlugin, mactime, PluginResult
from Registry.Registry import RegistryValueNotFoundException


class Plugin(BasePlugin):
    """Extracts the user's proxy settings"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        k = self.open_key(
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )
        if not k:
            return

        r = PluginResult(key=k)

        r.custom["type"] = "proxy"
        r.custom["enabled"] = self.safe_value(k, "ProxyEnabled", 0) == 1
        r.custom["proxy"] = self.safe_value(k, "ProxyServer", "N/A")
        r.custom["exceptions"] = self.safe_value(k, "ProxyOverride", "")

        yield r

        r = PluginResult(key=k)
        r.custom["type"] = "autoconfig"
        r.custom["proxypac"] = self.safe_value(k, "AutoConfigURL", "N/A")

        yield r

    def display_human(self, r):
        if r.custom["type"] == "proxy":
            print("[PROXY]")
            print(f"\tEnabled: {r.custom['enabled']}")
            print(f"\tProxy URL: {r.custom['proxy']}")
            print(f"\tExceptions: {r.custom['exceptions']}")
        elif r.custom["type"] == "autoconfig":
            print("[AUTO-CONFIG]")
            print(f"\tProxyPac URL: {r.custom['proxypac']}")
        print()

    def display_machine(self, r):
        print(mactime(name="Proxy settings modified", mtime=r.mtime))

    def safe_value(self, k, name, default):
        for v in k.values():
            if v.name() == name:
                return v.value()
        return default
