# Plugin written by Tim Taylor, timtaylor3@yahoo.com
from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Returns the user names with sids"""

    __REGHIVE__ = "SOFTWARE"

    def run(self):
        path = r"Microsoft\Windows NT\CurrentVersion\ProfileList"
        key = self.open_key(path)
        if not key:
            return

        sid_list = list()

        for v in key.subkeys():
            sid_list.append(v.name())

        for sid in sid_list:
            sid_path = path + "\\" + sid
            key2 = self.open_key(sid_path)

            if not key2:
                continue

            for entry in key2.values():
                if entry.name() == "ProfileImagePath":
                    res = PluginResult(key=key, value=entry)
                    user_name = entry.value().split("\\")[-1]
                    res.custom["value"] = "{}:\t{}".format(user_name, key2.name())
                    yield res

    def display_human(self, result):
        print(result.custom["value"])

    def display_machine(self, result):
        print(mactime(name=result.custom["value"], mtime=result.mtime))
