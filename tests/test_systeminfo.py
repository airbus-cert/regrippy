from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegSZ, RegBin
import pytest

from regrippy.plugins.systeminfo import Plugin as plugin

@pytest.fixture
def mock_system():
    def mock_reg():

        key = RegistryKeyMock.build("ControlSet001")

        key_hostname = RegistryKeyMock("Control\\ComputerName\\ComputerName", key)
        key_shutdowntime = RegistryKeyMock("Control\\Windows", key)
        key_ipaddress = RegistryKeyMock("Services\\Tcpip\Parameters\\Interfaces", key)

        key.add_child(key_hostname)
        key.add_child(key_shutdowntime)
        key.add_child(key_dhcpipaddress)
        key.add_child(key_ipaddress)

        val1 = RegistryValueMock(key_hostname, "TestPC", RegSZ)
        val2 = RegistryValueMock(key_shutdowntime, b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)
        val3 = RegistryValueMock(key_dhcpipaddress, "127.0.0.1", RegSZ)
        val4 = RegistryValueMock(key_ipaddress, "127.0.0.2", RegSZ)

        key.add_value(val1)
        key.add_value(val2)
        key.add_value(val3)
        key.add_value(val4)

        reg = RegistryMock("SYSTEM", "system", key.root())
        reg.set_ccs(1)

def mock_software():
    def mock_reg():
        key = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion")

        val1 = RegistryValueMock("InstallDate", b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)
        val2 = RegistryValueMock("RegisteredOwner", "AnyOwner", RegSZ)
        val3 = RegistryValueMock("ProductName", "Windows 7 Professional", RegSZ)

        key.add_value(val1)
        key.add_value(val2)
        key.add_value(val3)

        return reg

    def test_systeminfo(mock_reg):
        # SOFTWARE
        # p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
        # results = list(p.run())

        # assert (len(results) == 2), "There should be  results, one per key"
        """
        for r in results:
            assert (r.value_name == "autorun"), f"Program label for {r.key_path} should be autorun"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
        """

        # SYSTEM
        p = plugin(mock_system, LoggerMock(), "SYSTEM", "-")
        results = list(p.run())

        assert (len(results) == 4), "There should be 4 results, one per key"
        """
        for r in results:
            assert (r.value_name == "autorun"), f"Program label for {r.key_path} should be autorun"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
        """
