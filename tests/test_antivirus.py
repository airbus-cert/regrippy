import pytest
from Registry.Registry import RegDWord, RegSZ

from regrippy.plugins.antivirus import Plugin as plugin

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock, RegistryValueMock


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        r"Microsoft\Security Center\Provider\Av\{D68DDC3A-831F-4fae-9E44-DA132C1ACF46}"
    )
    reg = RegistryMock("SOFTWARE", "software", key.root())

    key.add_value(RegistryValueMock("DISPLAYNAME", "Antivirus Windows Defender", RegSZ))
    key.add_value(
        RegistryValueMock("GUID", "{D68DDC3A-831F-4fae-9E44-DA132C1ACF46}", RegSZ)
    )
    key.add_value(RegistryValueMock("PRODUCTEXE", "windowsdefender://", RegSZ))
    key.add_value(
        RegistryValueMock(
            "REPORTINGEXE", "%ProgramFiles%\\Windows Defender\\MsMpeng.exe", RegSZ
        )
    )
    key.add_value(RegistryValueMock("STATE", 0x61100, RegDWord))

    return reg


def test_antivirus(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")

    results = list(p.run())

    assert len(results) == 1, "There should be a single result"
    assert (
        results[0].custom["DisplayName"] == "Antivirus Windows Defender"
    ), "The extracted antivirus name must be 'Antivirus Windows Defender'"
    assert (
        results[0].custom["State"] == "ON | UP_TO_DATE | MICROSOFT_PRODUCT"
    ), "The state must match the following: enabled, up-to-date Microsoft antivirus"
