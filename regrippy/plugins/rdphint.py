from regrippy import BasePlugin, PluginResult, mactime
from Registry import Registry


class Plugin(BasePlugin):
    """Lists the recently connected to RDP servers"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        key = self.open_key(r"Software\Microsoft\Terminal Server Client\Servers")
        if not key:
            return

        for subkey in key.subkeys():
            try:
                username = subkey.value("UsernameHint").value()
            except Registry.RegistryValueNotFoundException:
                username = ""

            res = PluginResult(key=subkey, value=None)
            res.custom["username"] = username
            yield res

    def display_human(self, result):
        print(f"{result.custom['username']}@{result.key_name}")

    def display_machine(self, result):
        print(
            mactime(
                name=f"{self.guess_username()} {result.custom['username']}@{result.key_name}",
                mtime=result.mtime,
            )
        )
