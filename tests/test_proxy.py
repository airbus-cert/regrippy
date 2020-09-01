import pytest
from Registry.Registry import RegDWord, RegSZ

from regrippy.plugins.proxy import Plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    # Add a normal proxy config
    url = RegistryValueMock("ProxyServer", "172.16.2.34:8080", RegSZ)
    enabled = RegistryValueMock("ProxyEnabled", 1, RegDWord)
    exceptions = RegistryValueMock("ProxyOverride", "10.0.0.0/8", RegSZ)

    key.add_value(url)
    key.add_value(enabled)
    key.add_value(exceptions)

    # Add a Proxy.pac
    pac = RegistryValueMock(
        "AutoConfigURL", "http://proxy.internal.corp/proxy.pac", RegSZ
    )

    key.add_value(pac)

    return reg


def test_proxy(mock_reg):
    p = Plugin(mock_reg, LoggerMock, "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 2, "There should be 2 results: a simple proxy and a proxypac"

    proxy = [x for x in results if x.custom["type"] == "proxy"][0]
    pac = [x for x in results if x.custom["type"] == "autoconfig"][0]

    assert proxy.custom["enabled"], "Proxy should be enabled"
    assert (
        proxy.custom["proxy"] == "172.16.2.34:8080"
    ), "Proxy should be set to '172.16.2.34:8080'"
    assert (
        proxy.custom["exceptions"] == "10.0.0.0/8"
    ), "There should be a single exception"

    assert (
        pac.custom["proxypac"] == "http://proxy.internal.corp/proxy.pac"
    ), "The ProxyPAC should be properly configured"
