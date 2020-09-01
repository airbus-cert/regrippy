import pytest
from Registry.Registry import RegBin

from regrippy.plugins.localusers import Plugin as plugin

from .reg_mock import LoggerMock, RegistryKeyMock, RegistryMock


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("SAM\\Domains\\Account\\Users\\Names")
    reg = RegistryMock("SAM", "sam", key.root())

    user1 = RegistryKeyMock("JohnDoe", key)
    user2 = RegistryKeyMock("JaneDoe", key)

    key.add_child(user1)
    key.add_child(user2)

    return reg


def test_localusers(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SAM", "-")

    results = list(p.run())
    assert len(results) == 2, "There should be two results"

    assert any(
        [x.key_name == "JohnDoe" for x in results]
    ), "There should be a user named 'JohnDoe'"
    assert any(
        [x.key_name == "JaneDoe" for x in results]
    ), "There should be a user named 'JaneDoe'"
