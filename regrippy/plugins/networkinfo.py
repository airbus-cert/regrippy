# Plugin written by Tim Taylor, timtaylor3@yahoo.com
from datetime import datetime
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
                guid_path = reg_interfaces + '\\' + guid
                key3 = self.open_key(guid_path)

                if not key3:
                    continue

                counter = 1
                for v in key3.values():
                    res = PluginResult(key=key3, value=v)

                    if counter == 1:
                        counter = 2
                        res.custom['value'] = "Settings for the adapter with a guid {}".format(guid)

                    if v.name() in ["Domain",
                                    "EnableDHCP",
                                    "DhcpNetworkHint",
                                    "DhcpDomain",
                                    "DhcpDomainSearchList",
                                    "DhcpServer",
                                    "DhcpIPAddress", "IPAddress",
                                    "DhcpSubnetMask", "SubnetMask", "DhcpSubnetMaskOpt",
                                    "DhcpConnForceBroadcastFlag",
                                    "DhcpGatewayHardwareCount",
                                    "DhcpNameServer",
                                    "NameServer",
                                    "UseZeroBroadcast",
                                    "EnableDeadGWDetect",
                                    "IsServerNapAware",
                                    "RegistrationEnabled",
                                    "RegisterAdapterName",
                                    "Lease",
                                    "AddressType",
                                    "MTU",
                                    "IPAutoconfigurationenabled",
                                    "UseZeroBroadcast"]:
                        res.custom['value'] = "{}: {}".format(v.name(), v.value())
                        yield res

                    if v.name() == "DhcpDefaultGateway":
                        lst_ips = v.value()
                        str_ip = [i for i in lst_ips if i]
                        str_ip = ', '.join(str_ip)
                        res.custom['value'] = "{}: {}".format(v.name(), str_ip)
                        yield res

                    if v.name() in ["LeaseObtainedTime", "LeaseTerminatesTime", "T1", "T2"]:
                        raw = datetime.utcfromtimestamp(v.value()).isoformat('T') + 'Z'
                        res.custom['value'] = "{0}:\t{1}".format(v.name(), raw)
                        yield res

                    '''
                    if v.name() == "DhcpGatewayHardware"
                        res.custom['value'] = "{}: {}".format(v.name(), v.value())
                        yield res
                    '''

                    '''
                    if v.name() == "DhcpInterfaceOptions":
                        res.custom['value'] = "{}: {}".format(v.name(), v.value())
                        yield res
                    '''

    def display_human(self, result):
        print("{0}".format(result.custom["value"]))

    def display_machine(self, result):
        print(mactime(name=result.custom['value'], mtime=result.mtime))