import pytest
from Registry.Registry import RegDWord

from regrippy.plugins.printer_history import Plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)

PRINTERS = [
    "Microsoft Print To PDF",
    "Microsoft XPS Document Writer",
    "OneNote",
    "Fax",
    "Send To OneNote 2016",
    "MyEvilPrinter",
]


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(r"Printers\ConvertUserDevModesCount")
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    for v in PRINTERS:
        val = RegistryValueMock(v, 0x00000001, RegDWord)
        key.add_value(val)

    return reg


def test_printer_history(mock_reg):
    p = Plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == len(PRINTERS), f"There should be {len(PRINTERS)} results"

    for r in results:
        assert r.value_name in PRINTERS, "The printer name should be valid"
