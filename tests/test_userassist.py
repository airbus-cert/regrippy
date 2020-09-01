import pytest
from Registry.Registry import RegBin

from regrippy.plugins.userassist import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg_seven():
    key = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    guid = RegistryKeyMock("{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}", key)
    key.add_child(guid)

    count = RegistryKeyMock("Count", guid)
    guid.add_child(count)

    notepad = RegistryValueMock(
        "{1NP14R77-02R7-4R5Q-O744-2RO1NR5198O7}\\abgrcnq.rkr",
        bytearray(
            [
                0x00,
                0x00,
                0x00,
                0x00,
                0x06,
                0x00,
                0x00,
                0x00,
                0x05,
                0x00,
                0x00,
                0x00,
                0x60,
                0xEA,
                0x00,
                0x00,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0x00,
                0x00,
                0x80,
                0xBF,
                0xFF,
                0xFF,
                0xFF,
                0xFF,
                0x02,
                0xD2,
                0x7E,
                0xCE,
                0xB4,
                0xBF,
                0xD4,
                0x01,
                0x00,
                0x00,
                0x00,
                00,
            ]
        ),
        RegBin,
    )
    count.add_value(notepad)

    return reg


@pytest.fixture
def mock_reg_xp():
    key = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    guid = RegistryKeyMock("{75048700-EF1F-11D0-9888-006097DEACF9}", key)
    key.add_child(guid)

    count = RegistryKeyMock("Count", guid)
    guid.add_child(count)

    notepad = RegistryValueMock(
        "HRZR_EHACNGU:P:\\JVAQBJF\\flfgrz32\\abgrcnq.rkr",
        bytearray(
            [
                0x01,
                0x00,
                0x00,
                0x00,
                0x08,
                0x00,
                0x00,
                0x00,
                0xC0,
                0x66,
                0x16,
                0xCE,
                0xA4,
                0xCE,
                0xD4,
                0x01,
            ]
        ),
        RegBin,
    )
    count.add_value(notepad)

    return reg


def test_userassist_win7(mock_reg_seven):
    p = plugin(mock_reg_seven, LoggerMock(), "NTUSER.DAT", "-")
    results = list(p.run())

    assert len(results) == 1, "There should be a single result"
    assert (
        "userassist" in results[0].custom.keys()
    ), "A 'userassist' object should have been created"

    ua = results[0].custom["userassist"]

    assert ua.name.endswith("\\notepad.exe"), "Decoded name should be notepad"
    assert ua.number_of_execs == 6, "Notepad was executed 6 times"
    assert ua.focus_count == 5, "Notepad was focused 5 times"
    assert ua.focus_time_secs == 0xEA60, "Notepad was focused for 60,000 seconds (!!)"


def test_userassist_winxp(mock_reg_xp):
    p = plugin(mock_reg_xp, LoggerMock(), "NTUSER.DAT", "-")
    results = list(p.run())

    assert len(results) == 1, "There should be a single result"
    assert (
        "userassist" in results[0].custom.keys()
    ), "A 'userassist' object should have been created"

    ua = results[0].custom["userassist"]

    assert ua.name.endswith("\\notepad.exe"), "Decoded name should be notepad"
    assert ua.number_of_execs == 3, "Notepad was executed 3 times"
