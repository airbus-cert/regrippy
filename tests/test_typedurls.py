import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.typedurls import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("Software\\Microsoft\\Internet Explorer\\TypedURLs")
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    url1 = RegistryValueMock("url1", "https://outlook.com", RegSZ)
    url2 = RegistryValueMock("url2", "https://airbus.com/order", RegSZ)

    key.add_value(url1)
    key.add_value(url2)

    return reg


def test_typedurls(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 2
    assert results[0].value_data == "https://outlook.com", "First URL should be Outlook"
    assert (
        results[1].value_data == "https://airbus.com/order"
    ), "Second URL should be Airbus"
