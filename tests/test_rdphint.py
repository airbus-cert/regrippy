import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.rdphint import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("Software\\Microsoft\\Terminal Server Client\\Servers")
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    srv1 = RegistryKeyMock("server1.com", key)
    srv2 = RegistryKeyMock("server2.com", key)

    key.add_child(srv1)
    key.add_child(srv2)

    srv1username = RegistryValueMock("UsernameHint", "root", RegSZ)
    srv1.add_value(srv1username)

    return reg


def test_rdphint(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 2, "There should only be 2 results"
    assert results[0].key_name == "server1.com", "First server should be server1.com"
    assert results[0].custom["username"] == "root", "First server should have user hint"
    assert results[1].key_name == "server2.com", "Second server should be server2.com"
    assert results[1].custom["username"] == "", "Second server should not have username"
