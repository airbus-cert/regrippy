# Plugin written by Tim Taylor, timtaylor3@yahoo.com
import binascii
import struct
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
                        yield res

                    if v.name() in ["Domain",
                                    "EnableDHCP",
                                    "DhcpNetworkHint",
                                    "DhcpDomain",
                                    "DhcpDomainSearchList",
                                    "DhcpServer",
                                    "DhcpIPAddress", "IPAddress",
                                    "DhcpSubnetMask",
                                    "DhcpConnForceBroadcastFlag",
                                    "DhcpDefaultGateway"
                                    "DhcpGatewayHardwareCount",
                                    "DhcpNameServer",
                                    "NameServer",
                                    "UseZeroBroadcast",
                                    "EnableDeadGWDetect",
                                    "IsServerNapAware",
                                    "RegistrationEnabled",
                                    "RegisterAdapterName",
                                    "Lease",
                                    "AddressType"
                                    "MTU",
                                    "IPAutoconfigurationenabled",
                                    "UseZeroBroadcast"]:
                        res.custom['value'] = "{}: {}".format(v.name(), v.value())
                        yield res

                    if v.name() == "DhcpSubnetMaskOpt":
                        lst_ips = v.value()
                        str_ip = [i for i in lst_ips if i]
                        str_ip = ', '.join(str_ip)
                        res.custom['value'] = "{}: {}".format(v.name(), str_ip)
                        yield res

                    if v.name() == "DhcpDefaultGateway":
                        lst_ips = v.value()
                        str_ip = [i for i in lst_ips if i]
                        str_ip = ', '.join(str_ip)
                        res.custom['value'] = "{}: {}".format(v.name(), str_ip)
                        yield res

                    if v.name() == "SubnetMask":
                        lst_ips = v.value()
                        str_ip = [i for i in lst_ips if i]
                        str_ip = ', '.join(str_ip)
                        res.custom['value'] = "{}: {}".format(v.name(), str_ip)
                        yield res

                    if v.name() == "LeaseObtainedTime":
                        lease_obtained_time = datetime.utcfromtimestamp(v.value()).isoformat('T') + 'Z'
                        res.custom['value'] = "LeaseObtainedTime: {0}".format(lease_obtained_time)
                        yield res

                    if v.name() == "LeaseTerminatesTime":
                        lease_terminates_time = datetime.utcfromtimestamp(v.value()).isoformat('T') + 'Z'
                        res.custom['value'] = "LeaseTerminatesTime: {0}".format(lease_terminates_time)
                        yield res

                    if v.name() == "T1":
                        t1 = datetime.utcfromtimestamp(v.value()).isoformat('T') + 'Z'
                        res.custom['value'] = "T1: {0}".format(t1)
                        yield res

                    if v.name() == "T2":
                        t2 = datetime.utcfromtimestamp(v.value()).isoformat('T') + 'Z'
                        res.custom['value'] = "T2: {0}".format(t2)
                        yield res

                    '''if v.name() == "DhcpGatewayHardware":
                        binary = binascii.hexlify(v.value())
                        res.custom['value'] = "DhcpGatewayHardware: {}".format(binary)
                        yield res'''

                    '''if v.name() == "DhcpInterfaceOptions":
                        binary = binascii.hexlify(v.value())
                        res.custom['value'] = "{}: {}".format(v.name(), binary)
                        yield res'''

    def display_human(self, result):
        print("{0}".format(result.custom["value"]))

    def display_machine(self, result):
        print(mactime(name=result.custom['value'], mtime=result.mtime))
