from regrippy import BasePlugin, PluginResult, mactime
# Not tested


class Plugin(BasePlugin):
    """Returns the computer's VSC Data"""
    __REGHIVE__ = "SYSTEM"

    def run(self):

        paths = [self.get_currentcontrolset_path() + r"\Services\VSS",
                 self.get_currentcontrolset_path() + r"\Services\VolSnap\MinDiffAreaFileSize",
                 self.get_currentcontrolset_path() + r"\Services\VSS\VssAccessControl",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToBackup",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToSnapshot",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToRestore",
                 ]

        for path in paths:
            key = self.open_key(path)
            if not key:
                continue

            for v in key.values():
                res = PluginResult(key=key, value=v)
                res.custom["Path"] = path
                res.custom["Value"] = v.value()
                yield res

    def display_human(self, result):
        if "VSS" in result.custom['Path']:
            print(r"{0}\{1} {2} {3}".format(result.custom['Path'], result.value_name, result.custom["Value"], result.mtime))
        else:
            print(r"{0}\{1} {2}".format(result.custom['Path'], result.value_name, result.mtime))

    def display_machine(self, result):
        if "VSS" in result.custom['Path']:
            print(mactime(name=f"{result.custom['Path']}\{result.value_name} {result.custom['Value']}", mtime=result.mtime))
        else:
            print(mactime(name=f"{result.custom['Path']}\{result.value_name}", mtime=result.mtime))
