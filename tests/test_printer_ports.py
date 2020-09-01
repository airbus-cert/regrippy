import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.printer_ports import Plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)

PORTS = [
    "COM1:",
    "COM2:",
    "FILE1:",
    "LPT1:",
    "LPT2:",
    "Ne00:",
    "Ne01:",
    "nul:",
    "PORTPROMPT:",
    "C:\\Windows\\System32\\hello.dll",
]


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(r"Microsoft\Windows NT\CurrentVersion\Ports")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    for v in PORTS:
        val = RegistryValueMock(v, "", RegSZ)
        key.add_value(val)

    return reg


def test_printer_ports(mock_reg):
    p = Plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")

    results = list(p.run())

    assert len(results) == len(PORTS), f"There should be {len(PORTS)} results"

    for r in results:
        assert r.value_name in PORTS, "The printer port should be valid"
