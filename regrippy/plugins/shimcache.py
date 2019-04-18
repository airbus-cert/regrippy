from regrippy import BasePlugin, PluginResult
from regrippy.thirdparty.ShimCacheParser import read_cache


class Plugin(BasePlugin):
    """Parse shim cache to show all executed binaries on machine"""
    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(self.get_currentcontrolset_path() + r"\Control\Session Manager\AppCompatCache") or \
              self.open_key(self.get_currentcontrolset_path() + r"\Control\Session Manager\AppCompatibility")

        if not key:
            return

        for entry in read_cache(key.value("AppCompatCache").value()):
            res = PluginResult(key=key, value=None)
            res.custom["date"] = entry[0]
            res.custom["path"] = entry[2]
            yield res

    def display_human(self, result):
        print(result.custom["date"] + "\t" + result.custom["path"])

