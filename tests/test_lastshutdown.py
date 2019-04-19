from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegBin
import pytest

from regrippy.plugins.lastshutdown import Plugin as plugin

@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("ControlSet001\\Control\\Windows")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    val = RegistryValueMock("ShutdownTime", b'\xe40\xa5!\xed\xf7\xd3\x01', RegBin)
    key.add_value(val)

    return reg


def test_lastshutdown(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SYSTEM", "-")

    results = list(p.run())
    assert(len(results) == 1), "There should be a single result"
    assert(results[0].custom["LastShutdownTime"] == "2018-05-30T08:06:36.766026Z"), "It should have returned 2018-05-30T08:06:36.766026Z"


