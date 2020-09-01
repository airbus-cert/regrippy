from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Searches for Sysinternal EulaAccepted keys"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(r"Software\Sysinternals")
        if not key:
            return

        for subkey in key.subkeys():
            eula = None
            for v in subkey.values():
                if v.name() == "EulaAccepted":
                    eula = v
                    break

            res = PluginResult(key=subkey, value=eula)
            yield res

    def display_human(self, result):
        print(result.key_name, "\t", result.value_data)
