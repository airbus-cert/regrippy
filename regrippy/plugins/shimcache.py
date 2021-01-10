from datetime import datetime

from regrippy import BasePlugin, PluginResult, mactime
from regrippy.thirdparty.ShimCacheParser import read_cache


class Plugin(BasePlugin):
    """Parse shim cache to show all executed binaries on machine"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(
            self.get_currentcontrolset_path()
            + r"\Control\Session Manager\AppCompatCache"
        ) or self.open_key(
            self.get_currentcontrolset_path()
            + r"\Control\Session Manager\AppCompatibility"
        )

        if not key:
            return

        for entry in read_cache(key.value("AppCompatCache").value()):
            timestamp = datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S")
            mtime = key.timestamp()
            path = entry[2].decode("utf8") if type(entry[2]) == bytes else entry[2]

            res = PluginResult(
                timestamp=timestamp,
                plugin="shimcache",
                mtime=mtime,
                key_name=key.name(),
                path=key.path(),
                custom={
                    'date': timestamp,
                    'path': path
                })
            yield res

    def display_human(self, result):
        print(result.custom["date"].strftime("%Y-%m-%d %H:%M:%S") + "\t" + result.custom["path"])

    def display_machine(self, result):
        date = result.custom["date"]
        atime = int(date.timestamp())

        print(mactime(name=result.custom["path"], mtime=result.mtime, atime=atime))
