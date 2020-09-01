import pytest
from Registry.Registry import RegBin

from regrippy.plugins.shimcache import Plugin as plugin
from tests.reg_mock import RegistryValueMock

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock

_entry_win10_ = (
    b"\x00" * 0x30
    + b"10ts"
    + b"\x00\x00\x00\x00\x2a\x01\x00\x00\x1c\x00t\x00e\x00s\x00t\x00_\x00s\x00h\x00i\x00m\x00c\x00a\x00c\x00h\x00e\x00\x1f\xb1\xb8\x6f\xaf\xf5\xd4\x01"
)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        "ControlSet001\\Control\\Session Manager\\AppCompatCache"
    )
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    val = RegistryValueMock("AppCompatCache", _entry_win10_, RegBin)
    key.add_value(val)

    return reg


def test_shimcache(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SYSTEM", "-")

    results = list(p.run())

    assert len(results) == 1, "There should only be 1 results"
    assert results[0].custom["path"] == "test_shimcache"
