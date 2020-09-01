import pytest
from Registry.Registry import RegDWord, RegSZ

from regrippy.plugins.sysinternals import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("Software\\Sysinternals")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    # Accepted
    sysmon = RegistryKeyMock("Sysmon", key)
    key.add_child(sysmon)
    sysmon_eula = RegistryValueMock("EulaAccepted", 1, RegDWord)
    sysmon.add_value(sysmon_eula)

    # Rejected
    procdump = RegistryKeyMock("Procdump", key)
    key.add_child(procdump)
    procdump_eula = RegistryValueMock("EulaAccepted", 0, RegDWord)
    procdump.add_value(procdump_eula)

    # No EulaAccepted
    procexp = RegistryKeyMock("Procexp", key)
    key.add_child(procexp)

    return reg


def test_sysinternals(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")

    results = list(p.run())

    assert len(results) == 3, "There should be 3 results"

    assert results[0].key_name == "Sysmon", "First result should be Sysmon"
    assert results[0].value_data == 1, "Sysmon should be 1 (accepted)"

    assert results[1].key_name == "Procdump", "Second result should be Procdump"
    assert results[1].value_data == 0, "Procdump should be 0 (refused)"

    assert results[2].key_name == "Procexp", "Third result should be Procexp"
    assert results[2].value_data == None, "Procexp shouldn't have a 'value'"
