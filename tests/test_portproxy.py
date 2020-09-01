import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.portproxy import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("ControlSet001\\Services\\PortProxy\\v4tov4")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    tcp = RegistryKeyMock("tcp", key)
    key.add_child(tcp)

    udp = RegistryKeyMock("udp", key)
    key.add_child(udp)

    https_proxy = RegistryValueMock("*/443", "127.0.0.1:1234", RegSZ)
    tcp.add_value(https_proxy)

    dns_proxy = RegistryValueMock("*/53", "8.8.8.8:80", RegSZ)
    udp.add_value(dns_proxy)

    return reg


def test_portproxy(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SYSTEM", "-")

    results = list(p.run())

    assert len(results) == 2, "There should be 2 results"

    for result in results:
        assert result.custom["proto"] in [
            "tcp",
            "udp",
        ], "The protocol should be either tcp or udp"

        if result.custom["proto"] == "tcp":
            assert result.value_name == "*/443", "The TCP portproxy FROM should be 443"
            assert (
                result.value_data == "127.0.0.1:1234"
            ), "The TCP portproxy TO should be 127.0.0.1:1234"
        else:  # UDP
            assert result.value_name == "*/53", "The UDP portproxy FROM should be 53"
            assert (
                result.value_data == "8.8.8.8:80"
            ), "The UDP portproxy TO should be 8.8.8.8:80"
