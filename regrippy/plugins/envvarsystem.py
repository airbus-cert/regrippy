from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Dump system environment variable"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(self.get_currentcontrolset_path() + r"\Control\Session Manager\Environment")
        if not key:
            return

        return (PluginResult(key=key, value=value) for value in key.values())
    
    def display_human(self, result):
        print("%s: %s" % (result.value_name, result.value_data))
    
    def display_machine(self, result):
        print(mactime(name="%s: %s" % (result.value_name, result.value_data), mtime=result.mtime))
