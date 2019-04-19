from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegSZ, RegBin
import pytest

from regrippy.plugins.systeminfo import Plugin as plugin


@pytest.fixture
def mock_software():
    key = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    key_install_date = RegistryKeyMock("InstallDate", key)
    key_owner = RegistryKeyMock("RegisteredOwner", key)
    key_product_name = RegistryKeyMock("ProductName", key)

    val1 = RegistryValueMock("InstallDate", 1523364100, RegBin)
    val2 = RegistryValueMock("RegisteredOwner", "Some Dude", RegSZ)
    val3 = RegistryValueMock("ProductName", "Windows 7 Professional", RegSZ)

    key.add_child(key_install_date)
    key.add_child(key_owner)
    key.add_child(key_product_name)

    key.add_value(val1)
    key.add_value(val2)
    key.add_value(val3)

    return reg


@pytest.fixture
def mock_system():
    key = RegistryKeyMock.build("ControlSet001")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    key_control = RegistryKeyMock("Control", key)
    key.add_child(key_control)

    key_hostname = RegistryKeyMock("ComputerName\\ComputerName", key)
    key_shutdown = RegistryKeyMock("Windows\\ShutdownTime", key)

    key.add_child(key_hostname)
    key.add_child(key_shutdown)

    val1 = RegistryValueMock(key_hostname, "SomeTestPCName", RegSZ)
    val2 = RegistryValueMock(key_shutdown, b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)

    key.add_value(val1)
    key.add_value(val2)

    key_interface = RegistryKeyMock("Services\\Tcpip\\Parameters\\Interfaces\\", key)
    key.add_child(key_interface)

    key_dhcp_ipaddress = RegistryKeyMock("{456A6A17D-21FC-123F-A689-A846D86EC008}\\DhcpIPAddress", key_interface)
    key_ip_address = RegistryKeyMock("{123ee342-7039-466e-9d20-806e6f6e6963}\\IPAddress", key_interface)

    key.add_child(key_dhcp_ipaddress)
    key.add_child(key_ip_address)

    val3 = RegistryValueMock(key_dhcp_ipaddress, '127.0.0.1', RegSZ)
    val4 = RegistryValueMock(key_ip_address, '127.0.0.2', RegSZ)

    key.add_value(val3)
    key.add_value(val4)

    return reg


def test_run(mock_system, mock_software ):
    # SOFTWARE
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert (len(results) == 3), "There should be  3 results."

    # SYSTEM
    p = plugin(mock_system, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())

    assert (len(results) == 4), "There should be 4 results"

