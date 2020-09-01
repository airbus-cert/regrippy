import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.filedialogmru import Plugin as plugin

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock, RegistryValueMock


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    # Open / Save
    opensavemru = RegistryKeyMock("OpenSaveMRU", key)
    key.add_child(opensavemru)

    osmru_list = RegistryValueMock("MRUList", "bar", RegSZ)
    osmru_b = RegistryValueMock("b", "evil.bat", RegSZ)
    osmru_a = RegistryValueMock("a", "LOVE-LETTER-FOR-YOU.TXT.vbs", RegSZ)
    osmru_r = RegistryValueMock("r", "quarterly_reports.docx", RegSZ)

    opensavemru.add_value(osmru_list)
    opensavemru.add_value(osmru_a)
    opensavemru.add_value(osmru_b)
    opensavemru.add_value(osmru_r)

    # Last visited
    lastvisitedmru = RegistryKeyMock("LastVisitedMRU", key)
    key.add_child(lastvisitedmru)

    lvmru_list = RegistryValueMock("MRUList", "ab", RegSZ)
    lvmru_a = RegistryValueMock("a", "%USERPROFILE%\\Desktop", RegSZ)
    lvmru_b = RegistryValueMock("b", "C:\\Temp", RegSZ)

    lastvisitedmru.add_value(lvmru_list)
    lastvisitedmru.add_value(lvmru_a)
    lastvisitedmru.add_value(lvmru_b)

    return reg


def test_filedialogmru(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 5, "There should be 5 results"

    assert results[0].value_data in [
        "evil.bat",
        "%USERPROFILE%\\Desktop",
    ], "The first result should be either from OpenSave or LastVisited"

    if results[0].value_data == "evil.bat":
        # OpenSaveMRU
        assert (
            results[1].value_data == "LOVE-LETTER-FOR-YOU.TXT.vbs"
        ), "The second result should be 'a'"
        assert (
            results[2].value_data == "quarterly_reports.docx"
        ), "The third result should be 'r'"

        # Then LastVisitedMRU
        assert (
            results[3].value_data == "%USERPROFILE%\\Desktop"
        ), "The fourth result shoul be 'a'"
        assert results[4].value_data == "C:\\Temp", "The fifth result shoul be 'b'"
    else:
        # LastVisitedMRU
        assert results[1].value_data == "C:\\Temp", "The second result shoul be 'b'"

        # Then OpenSaveMRU
        assert results[2].value_data == "evil.bat", "The third result shoul be 'b'"
        assert (
            results[3].value_data == "LOVE-LETTER-FOR-YOU.TXT.vbs"
        ), "The fourth result should be 'a'"
        assert (
            results[4].value_data == "quarterly_reports.docx"
        ), "The fifth result should be 'r'"
