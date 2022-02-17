import pytest

from regrippy.plugins.env import Plugin

from .reg_mock import (
    LoggerMock,
    RegistryKeyMock,
    RegistryMock,
    RegistryValueMock,
    RegSZ,
)


@pytest.fixture
def system_vars():
    return {
        "PATH": "C:\\Windows\\System32;C:\\Temp",
        "ComSpec": "C:\\Windows\\system32\\cmd.exe",
    }


@pytest.fixture
def mock_system_reg(system_vars):
    k = RegistryKeyMock.build("ControlSet001\\Control\\Session Manager\\Environment")
    r = RegistryMock("SYSTEM", "SYSTEM", k.root())
    r.set_ccs(1)

    for name, value in system_vars.items():
        reg_value = RegistryValueMock(name, value, RegSZ)
        k.add_value(reg_value)

    return r


def test_env(mock_system_reg, system_vars):
    # TODO: test the other locations
    p = Plugin(mock_system_reg, LoggerMock(), "SYSTEM", "-")
    results = list(p.run())

    assert len(results) == len(
        system_vars
    ), "All system environment variables should be found"
    assert set([x.custom["Name"] for x in results]) == set(
        [f"%{x}%" for x in system_vars.keys()]
    ), "System environment variable names don't match"
