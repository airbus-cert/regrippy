import pytest
from Registry.Registry import RegSZ

from regrippy.plugins.putty import Plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_reg():
    key = RegistryKeyMock.build("Software\\SimonTatham\\PuTTY")
    reg = RegistryMock("NTUSER.DAT", "ntuser.dat", key.root())

    sessions = RegistryKeyMock("Sessions", key)
    key.add_child(sessions)

    # Sample session to my-ssh-server.com
    sess_key = RegistryKeyMock("MySSH", sessions)
    sessions.add_child(sess_key)

    sess_key.add_value(RegistryValueMock("HostName", "my-ssh-server.com", RegSZ))
    sess_key.add_value(RegistryValueMock("Protocol", "ssh", RegSZ))

    # Host key to evil-server.eu
    ssh_hosts = RegistryKeyMock("SshHostKeys", key)
    key.add_child(ssh_hosts)

    ssh_hosts.add_value(
        RegistryValueMock("ecdsa@22:evil-server.eu", "0xbadc00ffee", RegSZ)
    )

    return reg


def test_putty(mock_reg):
    p = Plugin(mock_reg, LoggerMock(), "NTUSER.DAT", "-")

    results = list(p.run())

    sessions = [x for x in results if x.custom["type"] == "session"]
    host_keys = [x for x in results if x.custom["type"] == "sshkey"]

    assert len(sessions) == 1, "There should be a single saved session"
    assert len(host_keys) == 1, "There should be a single saved SSH key"

    session = sessions[0]
    host_key = host_keys[0]

    assert session.key_name == "MySSH", "The session's name should be 'MySSH'"
    assert (
        session.custom["host"] == "my-ssh-server.com"
    ), "The session should point to my-ssh-server.com"
    assert session.custom["protocol"] == "ssh", "The session should be using SSH"

    assert (
        host_key.custom["crypto"] == "ecdsa"
    ), "Host key should be detected as 'ecdsa'"
    assert (
        host_key.custom["host"] == "22:evil-server.eu"
    ), "Host for the saved key should be 'evil-server.eu'"
