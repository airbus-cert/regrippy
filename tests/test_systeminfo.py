from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegSZ, RegBin
import pytest

from regrippy.plugins.systeminfo import Plugin as plugin

@pytest.fixture
def mock_software():
    def mock_reg():
        key1 = RegistryKeyMock.build("ControlSet001\\Control\\ComputerName\\ComputerName")
        key2 = RegistryKeyMock.build("ControlSet001\\Control\\Windows")
        key3 = RegistryKeyMock.build("ControlSet001\\\Services\\Tcpip\Parameters\\Interfaces")
        key4 = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion")

        reg = RegistryMock("SYSTEM", "system", key1.root())
        reg = RegistryMock("SYSTEM", "system", key2.root())
        reg = RegistryMock("SYSTEM", "system", key3.root())
        reg = RegistryMock("SYSTEM", "system", key4.root())
        reg.set_ccs(1)

        val1 = RegistryValueMock("ComputerName", "TestPC", RegSZ)
        val2 = RegistryValueMock("InstallDate", b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)
        val3 = RegistryValueMock("RegisteredOwner", "AnyOwner", RegSZ)
        val4 = RegistryValueMock("ProductName", "Windows 7 Professional", RegSZ)
        val5 = RegistryValueMock("DhcpIPAddress", "127.0.0.1", RegSZ)
        val6 = RegistryValueMock("IPAddress", "127.0.0.2", RegSZ)
        val7 = RegistryValueMock("ShutdownTime", b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)

        key1.add_value(val1)
        key2.add_value(val2)
        key3.add_value(val3)
        key4.add_value(val4)
        key5.add_value(val5)
        key6.add_value(val5)
        key7.add_value(val6)

        return reg

    def test_systeminfo(mock_reg):
        # SOFTWARE
        p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
        results = list(p.run())

        assert (len(results) == 2), "There should be  results, one per key"
        """
        for r in results:
            assert (r.value_name == "autorun"), f"Program label for {r.key_path} should be autorun"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
        """

        # SYSTEM
        p = plugin(mock_ntuser, LoggerMock(), "SYSTEM", "-")
        results = list(p.run())

        assert (len(results) == 4), "There should be 4 results, one per key"
        """
        for r in results:
            assert (r.value_name == "autorun"), f"Program label for {r.key_path} should be autorun"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
            assert (r.value_data == "evil.exe"), f"Program path for {r.keypath} should be evil.exe"
        """
