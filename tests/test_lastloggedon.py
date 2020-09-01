import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.lastloggedon import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        "Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI"
    )
    reg = RegistryMock("SOFTWARE", "software", key.root())

    user = RegistryValueMock("LastLoggedOnUser", "MYDOMAIN\\User01", RegSZ)
    sam = RegistryValueMock("LastLoggedOnSAM", ".\\User02", RegSZ)
    provider = RegistryValueMock("LastLoggedOnProvider", "No", RegSZ)

    key.add_value(user)
    key.add_value(sam)
    key.add_value(provider)

    return reg


def test_lastloggedon(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert len(results) == 2, "There should be 2 results"
    assert set([r.value_name for r in results]) == set(
        ["LastLoggedOnUser", "LastLoggedOnSAM"]
    ), "The results should be User and SAM (no Provider)"
