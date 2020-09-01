# Plugin written by Tim Taylor, timtaylor3@yahoo.com
import struct
from datetime import datetime
from Registry.RegistryParse import parse_windows_timestamp
from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Return System Information"""

    __REGHIVE__ = ["SYSTEM", "SOFTWARE"]

    def run(self):
        if self.hive_name == "SYSTEM":

            reg_host_name = (
                self.get_currentcontrolset_path()
                + r"\Control\ComputerName\ComputerName"
            )
            reg_last_shutdown = self.get_currentcontrolset_path() + r"\Control\Windows"
            reg_interfaces = (
                self.get_currentcontrolset_path()
                + r"\Services\Tcpip\Parameters\Interfaces"
            )

            paths = [reg_host_name, reg_last_shutdown, reg_interfaces]

        else:  # SOFTWARE
            paths = [r"Microsoft\Windows NT\CurrentVersion"]

        for path in paths:
            key = self.open_key(path)

            if not key:
                continue

            for v in key.values():
                if v.name() == "ComputerName":
                    res = PluginResult(key=key, value=v)
                    hostname = v.value()
                    res.custom["value"] = "Hostname:\t\t{0}".format(hostname)
                    yield res

                if v.name() == "ShutdownTime":
                    binary = struct.unpack("<Q", v.value())[0]
                    dt = parse_windows_timestamp(binary)
                    last_shutdown = dt.isoformat("T") + "Z"
                    res = PluginResult(key=key, value=v)
                    res.custom["value"] = "Last Shutdown Time:\t{0}".format(
                        last_shutdown
                    )
                    yield res

                if v.name() == "InstallDate":
                    res = PluginResult(key=key, value=v)
                    install_date = (
                        datetime.utcfromtimestamp(v.value()).isoformat("T") + "Z"
                    )
                    res.custom["value"] = "Install Date:\t\t{0}".format(install_date)
                    yield res

                if v.name() == "RegisteredOwner":
                    res = PluginResult(key=key, value=v)
                    registered_owner = v.value()
                    res.custom["value"] = "Registered Owner:\t{0}".format(
                        registered_owner
                    )
                    yield res

                if v.name() == "ProductName":
                    res = PluginResult(key=key, value=v)
                    product_name = v.value()
                    res.custom["value"] = "Operating System:\t{0}".format(product_name)
                    yield res

            if path.endswith("Interfaces"):
                guid_list = list()
                for v in key.subkeys():
                    guid_list.append(v.name())

                for guid in guid_list:
                    guid_path = path + "\\" + guid
                    key2 = self.open_key(guid_path)

                    if not key2:
                        continue

                    for entry in key2.values():
                        if entry.name() == "IPAddress":
                            res = PluginResult(key=key, value=entry)
                            ip_address = entry.value()
                            if ip_address != "":
                                res.custom["value"] = "IP Address:\t\t{0}".format(
                                    ip_address
                                )
                                yield res

                        if entry.name() == "DhcpIPAddress":
                            res = PluginResult(key=key, value=entry)
                            ip_address = entry.value()
                            res.custom["value"] = "IP Address:\t\t{0}".format(
                                ip_address
                            )
                            if ip_address != "":
                                res.custom["value"] = "IP Address:\t\t{0}".format(
                                    ip_address
                                )
                                yield res

    def display_human(self, result):
        print("{0}".format(result.custom["value"]))

    def display_machine(self, result):
        print(mactime(name=f"{result.custom['value']}", mtime=result.mtime))
