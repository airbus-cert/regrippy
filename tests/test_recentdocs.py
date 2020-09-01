import pytest
from Registry.Registry import RegBin, RegSZ

from regrippy.plugins.recentdocs import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    mrulistex = RegistryValueMock("MRUListEx", b"random bytes", RegBin)
    key.add_value(mrulistex)

    document = RegistryValueMock(
        "a",
        b"m\x00y\x00d\x00o\x00c\x00u\x00m\x00e\x00n\x00t\x00.\x00d\x00o\x00c\x00x\x00\x00random_bytes\xCA\xFE",
        RegBin,
    )
    key.add_value(document)

    return reg


def test_recentdocs(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    assert len(results) == 1, "There should be a single result"
    assert (
        results[0].custom["docname"] == "mydocument.docx"
    ), "The document should be named 'mydocument.docx'"
