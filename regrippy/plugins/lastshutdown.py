# Plugin written by Tim Taylor, timtaylor3@yahoo.com
import struct
from Registry.RegistryParse import parse_windows_timestamp
from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Return the last shutdown time"""

    __REGHIVE__ = "SYSTEM"

    def run(self):

        key = self.open_key(self.get_currentcontrolset_path() + r"\Control\Windows")
        if not key:
            return

        for v in key.values():
            if v.name() == "ShutdownTime":
                binary = struct.unpack("<Q", v.value())[0]
                dt = parse_windows_timestamp(binary)
                value = dt.isoformat("T") + "Z"
                res = PluginResult(key=key, value=v)
                res.custom["LastShutdownTime"] = value
                yield res

    def display_human(self, result):
        print("Last Shutdown Time was: {0}".format(result.custom["LastShutdownTime"]))

    def display_machine(self, result):
        print(
            mactime(
                name=f"{result.value_name} {result.custom['LastShutdownTime']}",
                mtime=result.mtime,
            )
        )
