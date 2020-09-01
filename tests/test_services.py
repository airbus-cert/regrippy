import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.services import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("ControlSet002\\Services")
    reg = RegistryMock("SYSTEM", "system", key.root())
    reg.set_ccs(2)

    srv1 = RegistryKeyMock("Service1", key)
    key.add_child(srv1)
    srv1_image = RegistryValueMock(
        "ImagePath", "C:\\windows\\system32\\srv1.sys", RegSZ
    )
    srv1.add_value(srv1_image)

    srv2 = RegistryKeyMock("Service2", key)
    key.add_child(srv2)

    return reg


def test_services(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SYSTEM", "-")

    results = list(p.run())

    assert len(results) == 2, "There should be two results"

    assert (
        results[0].key_name == "Service1"
    ), "The first service should be named 'Service1'"
    assert (
        results[0].custom["image_path"] == "C:\\windows\\system32\\srv1.sys"
    ), "The first service's image path should match"

    assert (
        results[1].key_name == "Service2"
    ), "The second service should be named 'Service2'"
