from regrippy import BasePlugin, PluginResult, mactime
# TODO:  Create Test Case

class Plugin(BasePlugin):
    """Returns the computer's VSC Data"""

    """
    -------+----------------------------------------------------------------------------------------------------------------------------------+
    | Value |                                                           Description                                                            |
    +-------+----------------------------------------------------------------------------------------------------------------------------------+
    |     0 | Boot: Loaded by kernel loader. Components of the driver stack for the boot (startup) volume must be loaded by the kernel loader. |
    |     1 | System: Loaded by I/O subsystem. Specifies that the driver is loaded at kernel initialization.                                   |
    |     2 | Automatic: Loaded by Service Control Manager. Specifies that the service is loaded or started automatically.                     |
    |     3 | Manual: The service does not start until the user starts it manually, such as by using Services or Devices in Control Panel.     |
    |     4 | Disabled: Specifies that the service should not be started.                                                                      |
    +-------+----------------------------------------------------------------------------------------------------------------------------------+
    """

    __REGHIVE__ = "SYSTEM"

    def run(self):

        paths = [self.get_currentcontrolset_path() + r"\Services\VSS",
                 self.get_currentcontrolset_path() + r"\Services\VolSnap\MinDiffAreaFileSize",
                 self.get_currentcontrolset_path() + r"\Services\VSS\VssAccessControl",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToBackup",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToSnapshot",
                 self.get_currentcontrolset_path() + r"\Control\BackupRestore\FilesNotToRestore"
                 ]

        for path in paths:
            key = self.open_key(path)
            if not key:
                continue

            for v in key.values():
                res = PluginResult(key=key, value=v)
                res.custom["Path"] = path
                res.custom["Value"] = v.value()

                dt = key.timestamp()
                res.custom['Last Write Time'] = dt.isoformat('T') + 'Z'
                yield res

    def display_human(self, result):
        if "VSS" in result.custom['Path']:
            print(r"{0}\{1} {2} {3}".format(result.custom['Path'], result.value_name, result.custom["Value"],
                                            result.custom['Last Write Time']))
        else:
            print(r"{0}\{1} {2}".format(result.custom['Path'], result.value_name, result.custom['Last Write Time']))

    def display_machine(self, result):
        if "VSS" in result.custom['Path']:
            print(mactime(name=f"{result.custom['Path']}\{result.value_name} {result.custom['Value']}",
                          mtime=result.mtime))
        else:
            print(mactime(name=f"{result.custom['Path']}\{result.value_name}", mtime=result.mtime))
