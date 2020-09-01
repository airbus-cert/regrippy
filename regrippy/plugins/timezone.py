from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Returns the computer's timezone"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        ccs = self.get_currentcontrolset_path()
        if not ccs:
            return

        key = self.open_key(ccs + r"\Control\TimeZoneInformation")
        if not key:
            return

        value = key.value("TimeZoneKeyName")
        yield PluginResult(key=key, value=value)
