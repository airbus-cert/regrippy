from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Extract the local user list from the SAM database"""

    __REGHIVE__ = "SAM"

    def run(self):
        k = self.open_key("SAM\\Domains\\Account\\Users\\Names")
        if not k:
            return

        for user in k.subkeys():
            res = PluginResult(key=user, value=None)
            yield res

    def display_human(self, res):
        print(res.key_name)

    def display_machine(self, res):
        print(mactime(name=res.key_name, mtime=res.mtime))
