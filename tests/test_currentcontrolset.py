import pytest

from regrippy import BasePlugin

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock


@pytest.mark.parametrize("current", [1, 2, 9, 10, 99, 100])
def test_currentcontrolset_path_zero_pads_to_three_digits(current):
    key = RegistryKeyMock.build(f"ControlSet{current:03d}\\Marker")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(current)
    plugin = BasePlugin(reg, LoggerMock(), "SYSTEM", "-")

    path = plugin.get_currentcontrolset_path()

    assert path == f"ControlSet{current:03d}"
    assert reg.open(path + "\\Marker").name() == "Marker"
