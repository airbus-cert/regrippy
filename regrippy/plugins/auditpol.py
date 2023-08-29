from regrippy import BasePlugin, PluginResult, mactime
from struct import unpack
from collections import OrderedDict


POL = OrderedDict.fromkeys([
    'System',
    'Logon/Logoff',
    'Object Access',
    'Privilege Use',
    'Detailed Tracking',
    'Policy Change',
    'Account Management',
    'DS Access',
    'Account Logon'
])

POL['System'] = [
    'Security State Change',
    'Security System Extension',
    'System Integrity',
    'IPsec Driver',
    'Other System Events'
]

POL['Logon/Logoff'] = [
    'Logon',
    'Logoff',
    'Account Lockout',
    'IPsec Main Mode',
    'Special Logon',
    'IPsec Quick Mode',
    'IPsec Extended Mode',
    'Other Logon/Logoff Events',
    'Network Policy Server',
    'User/Device Claims',
    'Group Membership'
]

POL['Object Access'] = [
    'File System',
    'Registry',
    'Kernel Object',
    'SAM',
    'Other Object Access Events',
    'Certification Services',
    'Application Generated',
    'Handle Manipulation',
    'File Share',
    'Filtering Platform Packet Drop',
    'Filtering Platform Connection',
    'Detailed File Share',
    'Removable Storage',
    'Central Policy Staging'
]

POL['Privilege Use'] = [
    'Sensitive Privilege Use',
    'Other Privilege Use Events',
    'Non Sensitive Privilege Use'
]

POL['Detailed Tracking'] = [
    'Process Creation',
    'Process Termination',
    'DPAPI Activity',
    'RPC Events',
    'Plug and Play Events',
    'Token Right Adjusted Events'
]

POL['Policy Change'] = [
    'Audit Policy Change',
    'Authentication Policy Change',
    'Authorization Policy Change',
    'MPSSVC Rule-Level Policy Change',
    'Filtering Platform Policy Change',
    'Other Policy Change Events'
]

POL['Account Management'] = [
    'User Account Management',
    'Computer Account Management',
    'Security Group Management',
    'Distribution Group Management',
    'Application Group Management',
    'Other Account Management Events'
]

POL['DS Access'] = [
    'Directory Service Access',
    'Directory Service Changes',
    'Directory Service Replication',
    'Detailed Directory Service Replication'
]


POL['Account Logon'] = [
    'Credential Validation',
    'Kerberos Authentication Service',
    'Other Account Logon Events',
    'Kerberos Service Ticket Operations'
]


LOGTYPES = {0: 'No Auditing', 1: 'Success', 2: 'Failure', 3: 'Success/Failure'}

class Plugin(BasePlugin):
    """Get the advanced security audit policy settings"""

    __REGHIVE__ = "SECURITY"

    def _unpack(self, data, idx):
        return unpack('<H', data[idx:idx+2])[0]

    def run(self):
        key = self.open_key(r"Policy\PolAdtEv")
        if not key:
            return

        # default value
        data = key.value("")
        vdata = data.value()

        # According to
        # http://www.kazamiya.net/files/projects/PolAdtEv_Structure_en_rev4.pdf,
        # every version of Windows stores in an ordered array the categories,
        # and the number of subcatergories depend on the version of Windows.
        # The number of subcategories are stored in a footer structure, which
        # offset is stored in the header at offset 8 the first category always
        # starts at offset 12

        catCountOffset = self._unpack(vdata, 8)
        offset = 12
        subcatCount = OrderedDict.fromkeys(POL.keys())
        i = 0
        for ckey in POL.keys():
            subcatCount[ckey] = self._unpack(vdata, catCountOffset+i*2)
            i = i + 1

        currOffset = offset
        for cat, subcats in POL.items():
            for i in range(subcatCount[cat]):
                logtype = self._unpack(vdata, currOffset + 2*i)
                if logtype > 3:
                    raise Exception(f'Unexpected value {logtype}')
                status = LOGTYPES[logtype]
                res = PluginResult(key=key, value=data)
                res.custom['cat'] = cat
                res.custom['subcat'] = subcats[i]
                res.custom['status'] = status
                yield res
            currOffset = currOffset + 2*(i+1)

    def display_human(self, r):
        cat = f'{r.custom["cat"]}: {r.custom["subcat"]}'
        print(f'{cat.ljust(70)} {r.custom["status"]}')
