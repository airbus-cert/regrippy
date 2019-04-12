from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Produces a timeline of every key's last modification date"""
    __REGHIVE__ = "ALL"

    def run(self):
        key = self.reg.root()

        yield from self.dump(key)
    
    def dump(self, key):
        res = PluginResult(key=key)
        res.path = self.cleanup_path(res.path)
        yield res

        for subkey in key.subkeys():
            yield from self.dump(subkey)
    
    def cleanup_path(self, s):
        rm = "CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}"
        if s.startswith(rm):
            return s[len(rm):]
        return s
