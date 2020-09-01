import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.run import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_software():
    curver_run = RegistryKeyMock.build("Microsoft\\Windows\\CurrentVersion\\Run")
    reg = RegistryMock("SOFTWARE", "software", curver_run.root())

    curver = reg.open("Microsoft\\Windows\\CurrentVersion")
    curver_runonce = RegistryKeyMock("RunOnce", curver)
    curver.add_child(curver_runonce)

    policies = RegistryKeyMock.build("Policies\\Explorer\\Run").root().open("Policies")
    curver.add_child(policies)

    policies_run = reg.open(
        "Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run"
    )

    # Add a sample entry in each key
    for k in [curver_run, curver_runonce, policies_run]:
        v = RegistryValueMock("autorun", "evil.exe", RegSZ)
        k.add_value(v)

    return reg


@pytest.fixture
def mock_ntuser():
    curver_run = RegistryKeyMock.build(
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    )
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", curver_run.root())

    curver = reg.open("Software\\Microsoft\\Windows\\CurrentVersion")
    curver_runonce = RegistryKeyMock("RunOnce", curver)
    curver.add_child(curver_runonce)

    winnt = (
        RegistryKeyMock.build("Windows NT\\CurrentVersion\\Windows\\Run")
        .root()
        .open("Windows NT")
    )
    reg.open("Software\\Microsoft").add_child(winnt)

    winnt_run = reg.open(
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows\\Run"
    )

    # Add a sample entry in each key
    for k in [curver_run, curver_runonce, winnt_run]:
        v = RegistryValueMock("autorun", "evil.exe", RegSZ)
        k.add_value(v)

    return reg


def test_run(mock_software, mock_ntuser):
    # SOFTWARE
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert len(results) == 3, "There should be 3 results, one per key"
    for r in results:
        assert (
            r.value_name == "autorun"
        ), f"Program label for {r.key_path} should be autorun"
        assert (
            r.value_data == "evil.exe"
        ), f"Program path for {r.keypath} should be evil.exe"

    # NTUSER.DAT
    p = plugin(mock_ntuser, LoggerMock(), "NTUSER.DAT", "-")
    results = list(p.run())

    assert len(results) == 3, "There should be 3 results, one per key"
    for r in results:
        assert (
            r.value_name == "autorun"
        ), f"Program label for {r.key_path} should be autorun"
        assert (
            r.value_data == "evil.exe"
        ), f"Program path for {r.keypath} should be evil.exe"
