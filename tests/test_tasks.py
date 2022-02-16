import pytest

from regrippy.plugins.tasks import Plugin as plugin

from .reg_mock import (
    LoggerMock,
    RegBin,
    RegistryKeyMock,
    RegistryMock,
    RegistryValueMock,
    RegSZ,
)


def reg_hex_to_binary(reg_hex_str):
    if not reg_hex_str.startswith("hex:"):
        raise ValueError("hex string must start with 'hex:'")

    reg_hex_str = reg_hex_str[len("hex:") :]
    reg_hex_str = reg_hex_str.replace("\n", "").replace("\r", "").replace(" ", "")

    bytes = reg_hex_str.split(",")
    return bytearray([int(b, 16) for b in bytes])


@pytest.fixture
def mock_reg():
    k = RegistryKeyMock.build("Microsoft\\Windows NT\\CurrentVersion")
    r = RegistryMock("SOFTWARE", "SOFTWARE", k.root())

    # Set Windows version to Windows 7
    # TODO: create a mock registry from a Windows 10 sample (they have more information in the registry)
    k.add_value(RegistryValueMock("CurrentBuild", "7601", RegSZ))

    # Prepare the "TaskCache" key and its children
    schedule = RegistryKeyMock("Schedule", k)
    k.add_child(schedule)

    taskcache = RegistryKeyMock("TaskCache", schedule)
    schedule.add_child(taskcache)

    tasks = RegistryKeyMock("Tasks", taskcache)
    taskcache.add_child(tasks)

    plain = RegistryKeyMock("Plain", taskcache)
    taskcache.add_child(plain)

    # Create a couple scheduled tasks
    ## Mozilla Firefox's Check Default Browser
    guid = "{3DC1692F-C720-4D79-BC69-9032ABF0CB22}"
    path = "\\Mozilla\\Firefox Default Browser Agent 308046B0AF4A39CB"
    dynamic_info = reg_hex_to_binary(
        "hex:03,00,00,00,05,08,de,1b,01,f0,d7,01,9f,28,ba,bc,14,23,d8,01,\
  00,00,00,00,00,00,00,00"
    )
    triggers = reg_hex_to_binary(
        "hex:15,00,00,00,00,00,00,00,00,1b,97,01,00,00,00,00,00,6d,df,f7,00,\
  f0,d7,01,00,1b,97,01,00,00,00,00,ff,ff,ff,ff,ff,ff,ff,ff,48,21,41,00,48,48,\
  48,48,80,e3,dd,5d,48,48,48,48,00,48,48,48,48,48,48,48,00,48,48,48,48,48,48,\
  48,01,00,00,00,48,48,48,48,1c,00,00,00,48,48,48,48,01,05,00,00,00,00,00,05,\
  15,00,00,00,a7,33,50,76,4e,9e,21,69,fe,d5,fb,78,e9,03,00,00,48,48,48,48,1a,\
  00,00,00,48,48,48,48,4a,00,6f,00,68,00,6e,00,2d,00,50,00,43,00,5c,00,4a,00,\
  6f,00,68,00,6e,00,00,00,48,48,48,48,48,48,38,00,00,00,48,48,48,48,58,02,00,\
  00,10,0e,00,00,34,08,00,00,ff,ff,ff,ff,07,00,00,00,00,00,00,00,00,00,00,00,\
  00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\
  00,00,00,dd,dd,00,00,00,00,00,00,00,1b,97,01,00,00,00,00,00,6d,df,f7,00,f0,\
  d7,01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\
  00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,ff,ff,ff,ff,01,00,00,00,\
  01,00,00,00,00,00,00,00,00,01,00,00,01,00,00,00,00,00,00,00,00,00,00,00"
    )
    hash = reg_hex_to_binary(
        "hex:67,2c,f8,7b,8e,f1,20,d1,7b,69,47,f3,9b,e3,c1,a6,53,5d,25,6d,71,3d,\
  38,97,2e,69,63,e9,85,61,74,15"
    )

    task_k = RegistryKeyMock(guid, tasks)
    tasks.add_child(task_k)
    task_k.add_value(RegistryValueMock("DynamicInfo", dynamic_info, RegBin))
    task_k.add_value(RegistryValueMock("Hash", hash, RegBin))
    task_k.add_value(RegistryValueMock("Path", path, RegSZ))
    task_k.add_value(RegistryValueMock("Triggers", triggers, RegBin))

    task_k = RegistryKeyMock(guid, plain)
    plain.add_child(task_k)

    return r


def test_tasks(mock_reg):
    p = plugin(mock_reg, LoggerMock(), "SOFTWARE", "-")

    results = list(p.run())

    assert len(results) == 1, "There should only be a single result"
    assert (
        results[0].custom["Path"]
        == "%System32%\\Tasks\\Mozilla\\Firefox Default Browser Agent 308046B0AF4A39CB"
    ), "The Task file path should be correctly parsed"
    assert results[0].custom["Actions"]
