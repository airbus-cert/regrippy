from binascii import unhexlify

import pytest
from Registry.Registry import RegBin, RegExpandSZ

from regrippy.plugins.localgroups import Plugin as plugin

from .reg_mock import (LoggerMock, RegistryKeyMock, RegistryMock,
                       RegistryValueMock)


@pytest.fixture
def mock_software():
    key = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion\\ProfileList")
    reg = RegistryMock("SOFTWARE", "software", key.root())

    user1 = RegistryKeyMock("S-1-5-21-2000-2000-2000-1001", key)
    user1profile = RegistryValueMock(
        "ProfileImagePath", "C:\\Users\\Arioch", RegExpandSZ
    )
    user1.add_value(user1profile)
    user2 = RegistryKeyMock("S-1-5-21-2000-2000-2000-1002", key)
    user2profile = RegistryValueMock(
        "ProfileImagePath", "C:\\Users\\Elric", RegExpandSZ
    )
    user2.add_value(user2profile)
    user3 = RegistryKeyMock("S-1-5-21-424242-424242-424242-1337", key)
    user3profile = RegistryValueMock(
        "ProfileImagePath", "C:\\Users\\Corum", RegExpandSZ
    )
    user3.add_value(user3profile)

    key.add_child(user1)
    key.add_child(user2)
    key.add_child(user3)

    return reg


@pytest.fixture
def mock_sam():
    key_machine = RegistryKeyMock.build("SAM\\Domains")
    reg = RegistryMock("SAM", "sam", key_machine.root())

    key_account = RegistryKeyMock("Account", key_machine)

    # Filler + machine SID that translates to S-1-5-21-2000-2000-2000
    machinevdata = "42" * 190 + "010400000000000515000000D0070000D0070000D0070000"

    machinev = RegistryValueMock("V", unhexlify(machinevdata), RegBin)
    key_account.add_value(machinev)

    key_machine.add_child(key_account)

    key_users = RegistryKeyMock("Users", key_account)
    key_account.add_child(key_users)

    key_names = RegistryKeyMock("Names", key_users)

    user1 = RegistryKeyMock("Administrator", key_users)
    user1value = RegistryValueMock("(default)", b"\x00\x00\x00\x00", 0x1F4)
    user1.add_value(user1value)
    user2 = RegistryKeyMock("Arioch", key_users)
    user2value = RegistryValueMock("(default)", b"\x00\x00\x00\x00", 0x3E9)
    user2.add_child(user2value)
    user3 = RegistryKeyMock("Elric", key_users)
    user3value = RegistryValueMock("(default)", b"\x00\x00\x00\x00", 0x3EA)
    user3.add_value(user3value)

    key_users.add_child(user1)
    key_users.add_child(user2)
    key_users.add_child(user3)

    key_users.add_child(key_names)

    key_builtin = RegistryKeyMock("Builtin", key_machine)
    key_machine.add_child(key_builtin)

    key_aliases = RegistryKeyMock("Aliases", key_builtin)

    key_group_admins = RegistryKeyMock("00000220", key_aliases)
    # Header + 3 SIDs: Administrator, Arioch & Corum (see above)
    group_admins_cdata = (
        "20020000000000000000000000000000"
        "D00000001E00000000000000F0000000"
        "D600000000000000C801000000000000"
        "03000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000410064006D0069006E006900"
        "73007400720061007400650075007200"
        "730000004C006500730020006D006500"
        "6D006200720065007300200064007500"
        "2000670072006F007500700065002000"
        "410064006D0069006E00690073007400"
        "72006100740065007500720073002000"
        "64006900730070006F00730065006E00"
        "740020006400192075006E0020006100"
        "63006300E8007300200063006F006D00"
        "70006C00650074002000650074002000"
        "69006C006C0069006D0069007400E900"
        "2000E00020006C0019206F0072006400"
        "69006E00610074006500750072002000"
        "65007400200061007500200064006F00"
        "6D00610069006E006500000001050000"
        "0000000515000000D0070000D0070000"
        "D0070000F40100000105000000000005"
        "15000000D0070000D0070000D0070000"
        "E9030000010500000000000515000000"
        "32790600327906003279060039050000"
    )
    group_admins_cvalue = RegistryValueMock("C", unhexlify(group_admins_cdata), RegBin)
    key_group_admins.add_value(group_admins_cvalue)

    key_group_users = RegistryKeyMock("00000221", key_aliases)
    # Header + 2 SIDs: interactive, authenticated
    group_users_cdata = (
        "21020000000000000000000000000000"
        "00010000180000000000000018010000"
        "68010000000000008002000000000000"
        "02000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "00000000000000000000000000000000"
        "000000005500740069006C0069007300"
        "6100740065007500720073004C006500"
        "730020007500740069006C0069007300"
        "61007400650075007200730020006E00"
        "65002000700065007500760065006E00"
        "74002000700061007300200065006600"
        "66006500630074007500650072002000"
        "6400650020006D006F00640069006600"
        "690063006100740069006F006E007300"
        "20006100630063006900640065006E00"
        "740065006C006C006500730020006F00"
        "7500200069006E00740065006E007400"
        "69006F006E006E0065006C006C006500"
        "73002000E00020006C001920E9006300"
        "680065006C006C006500200064007500"
        "20007300790073007400E8006D006500"
        "A0003B00200070006100720020006100"
        "69006C006C0065007500720073002C00"
        "200069006C0073002000700065007500"
        "760065006E007400200065007800E900"
        "6300750074006500720020006C006100"
        "200070006C0075007000610072007400"
        "20006400650073002000610070007000"
        "6C00690063006100740069006F006E00"
        "73002E00010100000000000504000000"
        "01010000000000050B000000"
    )
    group_users_cvalue = RegistryValueMock("C", unhexlify(group_users_cdata), RegBin)
    key_group_users.add_value(group_users_cvalue)

    key_aliases.add_child(key_group_admins)
    key_aliases.add_child(key_group_users)

    key_builtin.add_child(key_aliases)

    return reg


def test_localgroups(mock_software, mock_sam):
    # SOFTWARE
    p = plugin(mock_software, LoggerMock(), "SOFTWARE", "-")
    results = list(p.run())

    assert (
        len(results) == 0
    ), "SOFTWARE run only builds internal data, yields no results"

    assert (
        len(p.user_profile_list) == 3
    ), "Three profiles should be parsed from the SOFTWARE hive"
    assert any(
        [profile["name"] == "Arioch" for profile in p.user_profile_list]
    ), 'There should be a user named "Arioch"'
    assert any(
        [profile["name"] == "Elric" for profile in p.user_profile_list]
    ), 'There should be a user named "Elric"'
    assert any(
        [profile["name"] == "Corum" for profile in p.user_profile_list]
    ), 'There should be a user named "Corum"'

    # SAM
    p = plugin(mock_sam, LoggerMock(), "SAM", "-")
    results = list(p.run())

    assert len(results) == 2, "SAM should contains 2 groups"

    group_admins = results[0].custom
    assert (
        group_admins["name"] == "Administrateurs"
    ), 'Group 1 should be "Administrateurs"'
    assert (
        group_admins["size"] == 3
    ), 'The "Administrateurs" group should have three members'
    user_sid_list = group_admins["member_sids"]
    assert (
        len(user_sid_list) == 3
    ), 'The "Administrateurs" groups should have three members'
    assert (
        user_sid_list[0] == "S-1-5-21-2000-2000-2000-500"
    ), "User 1 should be local SID + RID 500"
    assert (
        user_sid_list[1] == "S-1-5-21-2000-2000-2000-1001"
    ), "User 2 should be local SID + RID 1001"
    assert (
        user_sid_list[2] == "S-1-5-21-424242-424242-424242-1337"
    ), 'User 3 should be "domain" SID + RID 1337'

    group_users = results[1].custom
    assert group_users["name"] == "Utilisateurs", 'Group 2 should be "Utilisateurs"'
    assert group_users["size"] == 2, 'The "Utilisateurs" group should have two members'
    user_sid_list = group_users["member_sids"]
    assert len(user_sid_list) == 2, 'The "Utilisateurs" groups should have two members'
    assert user_sid_list[0] == "S-1-5-4", "User 1 should be local well-known SID 4"
    assert user_sid_list[1] == "S-1-5-11", "User 2 should be local well-known SID 11"
