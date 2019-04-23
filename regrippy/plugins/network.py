# Plugin written by Tim Taylor, timtaylor3@yahoo.com
import os
from Registry import Registry
from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Returns combined SYSTEM and SOFTWARE information regarding the network configuration"""
    __REGHIVE__ = ["SOFTWARE", "SYSTEM"]

    def run(self):
        path = os.path.split(self.hive_path)[0]
        sys_reg = os.path.join(path, "SYSTEM")
        soft_reg = os.path.join(path, "SOFTWARE")

        self.network_settings(sys_reg, soft_reg)

    def control_set_check(self, sys_reg):
        """
        Determine which Control Set the system was using
        """
        registry = Registry.Registry(sys_reg)
        key = registry.open("Select")
        for v in key.values():
            if v.name() == "Current":
                return v.value()

    def network_settings(self, sys_reg, soft_reg):
        """
        Network Settings
        """
        nic_names = []
        results_dict = {}
        nic_list = []
        nics_dict = {}
        int_list = []
        registry = Registry.Registry(soft_reg)
        key = registry.open("Microsoft\\Windows NT\\CurrentVersion\\NetworkCards")
        print(("=" * 51) + "\n[+] Network Adapters\n" + ("=" * 51))

        # Populate the subkeys containing the NICs information
        for v in key.subkeys():
            nic_list.append(v.name())

        for nic in nic_list:
            k = registry.open("Microsoft\\Windows NT\\CurrentVersion\\NetworkCards\\%s" % nic)
            for v in k.values():
                if v.name() == "Description":
                    desc = v.value()
                    nic_names.append(desc)
                if v.name() == "ServiceName":
                    guid = v.value()
            nics_dict['Description'] = desc
            nics_dict['ServiceName'] = guid

        reg = Registry.Registry(sys_reg)
        key2 = reg.open("ControlSet00%s\\services\\Tcpip\\Parameters\\Interfaces" % self.control_set_check(sys_reg))
        # Populate the subkeys containing the interfaces GUIDs
        for v in key2.subkeys():
            int_list.append(v.name())

        def guid_to_name(g):
            for k, v in nics_dict.items():
                '''
                k = ServiceName, Description
                v = GUID, Adapter name
                '''
                if v == g:
                    return nics_dict['Description']

        # Grab the NICs info based on the above list
        for i in int_list:
            print("[-] Interface........: %s" % guid_to_name(i))
            print("[-] GUID.............: %s" % i)
            key3 = reg.open("ControlSet00%s\\services\\Tcpip\\Parameters\\Interfaces\\%s" % (self.control_set_check(sys_reg), i))
            for v in key3.values():
                if v.name() == "Domain":
                    results_dict['Domain'] = v.value()
                if v.name() == "IPAddress":
                    # Sometimes the IP would end up in a list here so just doing a little check
                    ip = v.value()
                    results_dict['IPAddress'] = ip[0]
                if v.name() == "DhcpIPAddress":
                    results_dict['DhcpIPAddress'] = v.value()
                if v.name() == "DhcpServer":
                    results_dict['DhcpServer'] = v.value()
                if v.name() == "DhcpSubnetMask":
                    results_dict['DhcpSubnetMask'] = v.value()

                    # Just to avoid key errors and continue to do becuase not all will have these fields
            if 'Domain' not in results_dict:
                results_dict['Domain'] = "N/A"
            if 'IPAddress' not in results_dict:
                results_dict['IPAddress'] = "N/A"
            if 'DhcpIPAddress' not in results_dict:
                results_dict['DhcpIPAddress'] = "N/A"
            if 'DhcpServer' not in results_dict:
                results_dict['DhcpServer'] = "N/A"
            if 'DhcpSubnetMask' not in results_dict:
                results_dict['DhcpSubnetMask'] = "N/A"

            print("[-] Domain...........: %s" % results_dict['Domain'])
            print("[-] IP Address.......: %s" % results_dict['IPAddress'])
            print("[-] DHCP IP..........: %s" % results_dict['DhcpIPAddress'])
            print("[-] DHCP Server......: %s" % results_dict['DhcpServer'])
            print("[-] DHCP Subnet......: %s" % results_dict['DhcpSubnetMask'])
            print("\n")


    def display_human(self, result):
        print(result.custom['value'])

    def display_machine(self, result):
        print(mactime(name=result.custom['value'], mtime=result.mtime))

