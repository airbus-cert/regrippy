import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.runmru import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    mru_list = RegistryValueMock("MRUList", "bca", RegSZ)
    key.add_value(mru_list)

    a = RegistryValueMock("a", "third result", RegSZ)
    b = RegistryValueMock("b", "first result", RegSZ)
    c = RegistryValueMock("c", "second result", RegSZ)

    key.add_value(a)
    key.add_value(b)
    key.add_value(c)

    return reg


def test_runmru(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 3, "There should be 3 results"

    assert results[0].value_name == "b", "The first result key should be 'b'"
    assert (
        results[0].value_data == "first result"
    ), "The first result should be 'first result'"

    assert results[1].value_name == "c", "The second result key should be 'c'"
    assert (
        results[1].value_data == "second result"
    ), "The second result should be 'second result'"

    assert results[2].value_name == "a", "The third result key should be 'a'"
    assert (
        results[2].value_data == "third result"
    ), "The third result should be 'third result'"
