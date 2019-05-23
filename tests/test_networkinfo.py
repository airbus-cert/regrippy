from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegSZ, RegBin
import pytest

from regrippy.plugins.networkinfo import Plugin as plugin


@pytest.fixture
def mock_software():
    key = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion\\NetworkCards\\1150")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    key.add_child("Description")
    key.add_child("Service Name")

    key_description = RegistryValueMock("Description", "Intel(R) PRO/1000 MT Desktop Adapter1", RegSZ)
    key_service_name = RegistryValueMock("Service Name", "{43A6A97D-21FC-461F-B689-A890D86EC010}", RegSZ)

    key.add_value(key_description)
    key.add_value(key_service_name)

    return reg


@pytest.fixture
def mock_system():
    interface1 = RegistryKeyMock.build("ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces\\{43A6A97D-21FC-461F-B689-A890D86EC010}")
    reg = RegistryMock("SYSTEM", "system", interface1.root())
    reg.set_ccs(1)

    val1 = RegistryValueMock('DhcpIPAddress', '127.0.0.1', RegSZ)
    val2 = RegistryValueMock('IPAddress', '127.0.0.2', RegSZ)
    val3 = RegistryValueMock('DhcpSubnetMask', '255.255.255.0', RegSZ)
    val4 = RegistryValueMock('DhcpServer', '10.10.10.2', RegSZ)
    val5 = RegistryValueMock('DhcpConnForceBroadcastFlag', 0, RegSZ)
    val6 = RegistryValueMock('DhcpDomain', 'test.domain.com', RegSZ)
    val7 = RegistryValueMock('DhcpNameServer', '192.168.0.1 192.168.1.1', RegSZ)
    val8 = RegistryValueMock('DhcpDefaultGateway', ['192.168.0.2', '', ''],  RegSZ)
    val9 = RegistryValueMock('DhcpSubnetMaskOpt', '255.255.255.0', RegSZ)
    val10 = RegistryValueMock('UseZeroBroadcast', 0, RegSZ)
    val11 = RegistryValueMock('EnableDeadGWDetect', 1, RegSZ)
    val12 = RegistryValueMock('EnableDHCP', 1, RegSZ)
    val13 = RegistryValueMock('NameServer', 'test_name_server', RegSZ)
    val14 = RegistryValueMock('Domain', 'test.domain', RegSZ)
    val15 = RegistryValueMock('RegistrationEnabled', 1, RegSZ)
    val16 = RegistryValueMock('RegisterAdapterName', 0, RegSZ)
    val17 = RegistryValueMock('Lease', 86400, RegSZ)
    val18 = RegistryValueMock('IsServerNapAware', 0, RegSZ)
    val19 = RegistryValueMock('LeaseObtainedTime', 1527776701, RegSZ)
    val20 = RegistryValueMock('T1', 1527776701, RegSZ)
    val21 = RegistryValueMock('T2', 1527776701, RegSZ)
    val22 = RegistryValueMock('LeaseTerminatesTime', 1527776701, RegSZ)

    interface1.add_value(val1)
    interface1.add_value(val2)
    interface1.add_value(val3)
    interface1.add_value(val4)
    interface1.add_value(val5)
    interface1.add_value(val6)
    interface1.add_value(val7)
    interface1.add_value(val8)
    interface1.add_value(val9)
    interface1.add_value(val10)
    interface1.add_value(val11)
    interface1.add_value(val12)
    interface1.add_value(val13)
    interface1.add_value(val14)
    interface1.add_value(val15)
    interface1.add_value(val16)
    interface1.add_value(val17)
    interface1.add_value(val18)
    interface1.add_value(val19)
    interface1.add_value(val20)
    interface1.add_value(val21)
    interface1.add_value(val22)

    return reg


def test_networkinfo(mock_software, mock_system):

    # SOFTWARE NIC's
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert (len(results) == 2), "There should be 2 results"
    assert (results[0].value_data == "Intel(R) PRO/1000 MT Desktop Adapter1"), \
        "It should have returned 'Intel(R) PRO/1000 MT Desktop Adapter1'"
    assert (results[1].value_data == "{43A6A97D-21FC-461F-B689-A890D86EC010}"), \
        "It should have returned '{43A6A97D-21FC-461F-B689-A890D86EC010}'"

    # SYSTEM NIC configs
    p = plugin(mock_system, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert (len(results) == 22), "There should be 19 results"
    assert (results[0].custom["value"] == "DhcpIPAddress: 127.0.0.1"), "It should have returned 'DhcpIPAddress: 127.0.0.1'"
    assert (results[1].custom["value"] == "IPAddress: 127.0.0.2"), "It should have returned 'IP Address: 127.0.0.2'"
    assert (results[2].custom["value"] == "DhcpSubnetMask: 255.255.255.0"), "DhcpSubnetMask: 255.255.255.0'"
    assert (results[3].custom["value"] == "DhcpServer: 10.10.10.2"), "It should have returned 'DhcpServer: 10.10.10.2'"
    assert (results[4].custom["value"] == "DhcpConnForceBroadcastFlag: 0"), "It should have returned 'DhcpConnForceBroadcastFlag: 0'"
    assert (results[5].custom["value"] == "DhcpDomain: test.domain.com"), "It should have returned 'DhcpDomain: test.domain.com'"
    assert (results[6].custom["value"] == "DhcpNameServer: 192.168.0.1 192.168.1.1"), "It should have returned 'DhcpNameServer: 192.168.0.1 192.168.1.1'"
    assert (results[7].custom["value"] == "DhcpDefaultGateway: 192.168.0.2"), "It should have returned 'DhcpDefaultGateway: 192.168.0.2'"
    assert (results[8].custom["value"] == "DhcpSubnetMaskOpt: 255.255.255.0"), "It should have returned 'DhcpSubnetMaskOpt: 255.255.255.0'"
    assert (results[9].custom["value"] == "UseZeroBroadcast: 0")
    assert (results[10].custom["value"] == "EnableDeadGWDetect: 1")
    assert (results[11].custom["value"] == "EnableDHCP: 1")
    assert (results[12].custom["value"] == "NameServer: test_name_server")
    assert (results[13].custom["value"] == "Domain: test.domain")
    assert (results[14].custom["value"] == "RegistrationEnabled: 1")
    assert (results[15].custom["value"] == "RegisterAdapterName: 0")
    assert (results[16].custom["value"] == "Lease: 86400")
    assert (results[17].custom["value"] == "IsServerNapAware: 0")
    assert (results[18].custom["value"] == "LeaseObtainedTime:\t2018-05-31T14:25:01Z")
    assert (results[19].custom["value"] == "T1:\t2018-05-31T14:25:01Z")
    assert (results[20].custom["value"] == "T2:\t2018-05-31T14:25:01Z")
    assert (results[21].custom["value"] == "LeaseTerminatesTime:\t2018-05-31T14:25:01Z")

