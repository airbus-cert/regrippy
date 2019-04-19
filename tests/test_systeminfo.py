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
def mock_hostname():
    key = RegistryKeyMock.build("ControlSet001\\Control\\ComputerName\\ComputerName")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)
    val = RegistryValueMock("ComputerName", "TestPC", RegSZ)
    key.add_value(val)
    return reg

@pytest.fixture
def mock_shutdowntime():
    key = RegistryKeyMock.build("ControlSet001\\Control\\Windows")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)
    key.add_child('ShutdownTime')
    val = RegistryValueMock("ShutdownTime", b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)
    key.add_value(val)
    return reg


@pytest.fixture
def mock_interfaces():
    key = RegistryKeyMock.build("ControlSet001\\Services\\Tcpip\\Parameters\Interfaces")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    key.add_child("{456A6A17D-21FC-123F-A689-A846D86EC008}")
    key_interface1 = reg.open("ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces\\{456A6A17D-21FC-123F-A689-A846D86EC008}")
    key_interface1.add_child('DhcpIPAddress')
    val1 = RegistryValueMock('DhcpIPAddress', '127.0.0.1', RegSZ)
    key_interface1.add_value(val1)

    key.add_child("{123ee342-7039-466e-9d20-806e6f6e6963}")
    key_interface2 = reg.open("ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces\\{123ee342-7039-466e-9d20-806e6f6e6963}")
    key_interface2.add_child('IPAddress')
    val2 = RegistryValueMock('IPAddress', '127.0.0.2', RegSZ)
    key_interface2.add_value(val2)

    return reg


def test_run(mock_software, mock_hostname, mock_shutdowntime, mock_interfaces):
    # SOFTWARE
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert (len(results) == 3), "There should be  3 results."

    # SYSTEM
    p = plugin(mock_hostname, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert (len(results) == 1), "There should be 1 results"

    p = plugin(mock_shutdowntime, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert (len(results) == 1), "There should be 1 results"

    p = plugin(mock_interfaces, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert (len(results) == 1), "There should be 1 results"

