from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Gets the temporary SRUM data from the registry"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        key = self.open_key("Microsoft\\Windows\\CurrentVersion\\SRUM\\Extensions\\")
        if not key:
            return

        for extension_key in key.subkeys():
            v = extension_key.value("(default)")
            res = PluginResult(key=extension_key, value=v)
            yield res
