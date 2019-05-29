from Registry.Registry import RegistryValueNotFoundException

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """WDigest enable state (mimikatz)"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(self.get_currentcontrolset_path() + r"\Control\SecurityProviders\WDigest")
        if not key:
            return

        try:
            status = key.value("UseLogonCredential")
        except RegistryValueNotFoundException:
            return

        res = PluginResult(key=key, value=status)
        yield res
    
    def display_human(self, result):
        print(result.value_data)
    
    def display_machine(self, result):
        print(mactime(name=result.value_data, mtime=result.mtime))
