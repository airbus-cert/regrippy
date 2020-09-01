import pytest
from Registry.Registry import RegBin, RegSZ

from regrippy.plugins.systeminfo import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


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
def mock_control():
    host_name = RegistryKeyMock.build(
        "ControlSet001\\Control\\ComputerName\\ComputerName"
    )
    reg = RegistryMock("SYSTEM", "system", host_name.root())
    reg.set_ccs(1)

    val1 = RegistryValueMock("ComputerName", "TestPC", RegSZ)
    host_name.add_value(val1)

    current_control_set = reg.open("ControlSet001\\Control")
    current_control_set_window = RegistryKeyMock("Windows", current_control_set)
    current_control_set.add_child(current_control_set_window)

    val2 = RegistryValueMock("ShutdownTime", b"\xe40\xa5!\xed\xf7\xd3\x01", RegBin)
    current_control_set_window.add_value(val2)
    return reg


@pytest.fixture
def mock_services():
    interface1 = RegistryKeyMock.build(
        "ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces\\{456A6A17D-21FC-123F-A689-A846D86EC008}"
    )
    reg = RegistryMock("SYSTEM", "system", interface1.root())
    reg.set_ccs(1)

    val1 = RegistryValueMock("DhcpIPAddress", "127.0.0.1", RegSZ)
    interface1.add_value(val1)

    interface2 = reg.open("ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces")
    key_ip_address = (
        RegistryKeyMock.build("{123ee342-7039-466e-9d20-806e6f6e6963}\\IPAddress")
        .root()
        .open("{123ee342-7039-466e-9d20-806e6f6e6963}")
    )
    interface2.add_child(key_ip_address)

    val2 = RegistryValueMock("IPAddress", "127.0.0.2", RegSZ)
    key_ip_address.add_value(val2)

    return reg


def test_run(mock_software, mock_control, mock_services):
    # SOFTWARE
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert len(results) == 3, "There should be  3 results."
    assert (
        results[0].custom["value"] == "Install Date:\t\t2018-04-10T12:41:40Z"
    ), "It should have returned 'Install Date:\t\t2018-04-10T12:41:40Z'"
    assert (
        results[1].custom["value"] == "Registered Owner:\tSome Dude"
    ), "It should have returned 'Registered Owner\tSome Dude'"
    assert (
        results[2].custom["value"] == "Operating System:\tWindows 7 Professional"
    ), "It should have returned 'Operating System:\tWindows 7 Professional'"

    # SYSTEM Control path
    p = plugin(mock_control, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert len(results) == 2, "There should be 2 results"
    assert (
        results[0].custom["value"] == "Hostname:\t\tTestPC"
    ), "It should have returned 'Hostname:\t\tTestPC'"
    assert (
        results[1].custom["value"] == "Last Shutdown Time:\t2018-05-30T08:06:36.766026Z"
    ), "It should have returned 'Install Date:\t2018-04-10T12:41:40Z'"

    # SYSTEM services
    p = plugin(mock_services, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())
    assert len(results) == 2, "There should be 2 results"
    assert (
        results[0].custom["value"] == "IP Address:\t\t127.0.0.1"
    ), "It should have returned 'IP Address:\t127.0.0.1'"
    assert (
        results[1].custom["value"] == "IP Address:\t\t127.0.0.2"
    ), "It should have returned 'IP Address:\t\t127.0.0.2'"
