import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.compname import Plugin as plugin

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock, RegistryValueMock


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("ControlSet001\\Control\\ComputerName\\ComputerName")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(1)

    val = RegistryValueMock("ComputerName", "MyCoolPC", RegSZ)
    key.add_value(val)

    return reg


def test_compname(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SYSTEM", "-")

    results = list(p.run())

    assert len(results) == 1, "There should be a single result"
    assert (
        results[0].value_data == "MyCoolPC"
    ), "The extracted computer name should match 'MyCoolPC'"
