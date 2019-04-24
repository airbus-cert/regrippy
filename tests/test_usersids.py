from .reg_mock import RegistryMock, RegistryKeyMock, RegistryValueMock, LoggerMock
from Registry.Registry import RegSZ
import pytest

from regrippy.plugins.usersids import Plugin as plugin

@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\S-1-5-18")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    val = RegistryValueMock("ProfileImagePath", "systemprofile", RegSZ)
    key.add_value(val)

    return reg


def test_usersids(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")

    results = list(p.run())
    assert(len(results) == 1), "There should be a single result"
    assert(results[0].custom["value"] == "systemprofile:	S-1-5-18"), "systemprofile:	S-1-5-18"


