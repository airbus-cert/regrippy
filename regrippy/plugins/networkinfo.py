# Plugin written by Tim Taylor, timtaylor3@yahoo.com
from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    __REGHIVE__ = ["SOFTWARE", "SYSTEM"]

    def run(self):
        if self.hive_name == "SOFTWARE":
            path = "Microsoft\\Windows NT\\CurrentVersion\\NetworkCards"
            key = self.open_key(path)
            if not key:
                return

            nic_list = list()
            for v in key.subkeys():
                nic_list.append(v.name())

            for nic in nic_list:
                path = "".join(["Microsoft\\Windows NT\\CurrentVersion\\NetworkCards\\", nic])
                key2 = self.open_key(path)
                if not key2:
                    return

                desc = ''
                service_name = ''
                for v in key2.values():
                    res = PluginResult(key=key, value=v)
                    if v.name() == "Description":
                        desc = v.value()
                    if v.name() == "ServiceName":
                        service_name = v.value()

                    res.custom['value'] = "{}, {}".format(service_name, desc)
                yield res
        else:
            reg_interfaces = "".join([self.get_currentcontrolset_path(), r"\Services\Tcpip\Parameters\Interfaces"])
            key2 = self.open_key(reg_interfaces)
            if not key2:
                return

            interface_list = list()
            for v in key2.subkeys():
                interface_list.append(v.name())

            for guid in interface_list:
                guid_path = "".join([self.get_currentcontrolset_path(),
                                     "services\\Tcpip\\Parameters\\Interfaces\\",
                                     guid])

                key3 = self.open_key(guid_path)
                if not key3:
                    continue

                for v in key3.values():
                    res = PluginResult(key=key3, value=v)
                    if v.name() == "Domain":
                        res.custom['value'] = "Domain, {}".format(v.value())

                    if v.name() == "IPAddress":
                        res.custom['value'] = "IPAddress, {}".format(v.value())

                    if v.name() == "DhcpIPAddress":
                        res.custom['value'] = "IPAddress, {}".format(v.value())

                    if v.name() == "DhcpServer":
                        res.custom['value'] = "DhcpServer, {}".format(v.value())

                    if v.name() == "DhcpSubnetMask":
                        res.custom['value'] = "DhcpSubnetMask, {}".format(v.value())

                yield res

    def display_human(self, result):
        print(result.custom['value'])

    def display_machine(self, result):
        print(mactime(name=result.custom['value'], mtime=result.mtime))

