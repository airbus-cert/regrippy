import re

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """get all KB update installation status"""

    __REGHIVE__ = "SOFTWARE"

    STATUS_CODES = {
        0x0: "Absent",
        0x5: "Uninstall pending",
        0x10: "Resolving",
        0x20: "Resolved",
        0x30: "Staging",
        0x40: "Staged",
        0x50: "Superseded",
        0x60: "Install pending",
        0x65: "Partially installed",
        0x70: "Installed",
        0x80: "Permanent",
    }

    def run(self):
        k = self.open_key(
            r"Microsoft\Windows\CurrentVersion\Component Based Servicing\Packages"
        )
        if not k:
            return

        r = r"Package(_(?P<pkgnum>[0-9]+))?_for_(?P<kb>KB[0-9]+)"
        for subkey in k.subkeys():
            match = re.match(r, subkey.name())
            if not match:
                continue

            res = PluginResult(key=subkey)
            res.custom["kb"] = match.group("kb")
            res.custom["number"] = match.group("pkgnum")
            res.custom["status_code"] = subkey.value("CurrentState").value()
            res.custom["status"] = self.STATUS_CODES.get(
                res.custom["status_code"], "unknown"
            )

            yield res

    def display_human(self, res):
        if res.custom["number"]:
            print(
                f"{res.custom['kb']} (#{res.custom['number']}): {res.custom['status']} (0x{res.custom['status_code']:02x})"
            )
        else:
            print(
                f"{res.custom['kb']}: {res.custom['status']} (0x{res.custom['status_code']:02x})"
            )

    def display_machine(self, res):
        if res.custom["number"]:
            print(
                mactime(
                    mtime=res.mtime,
                    name=f"{res.custom['kb']} #{res.custom['number']} [{res.custom['status']}]",
                )
            )
        else:
            print(
                mactime(
                    mtime=res.mtime, name=f"{res.custom['kb']} [{res.custom['status']}]"
                )
            )
