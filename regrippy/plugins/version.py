from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Get the Windows version"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        key = self.open_key("Microsoft\\Windows NT\\CurrentVersion")
        if not key:
            return

        value = key.value("ProductName")
        yield PluginResult(key=key, value=value)

    def display_human(self, result):
        print(result.value_data)
