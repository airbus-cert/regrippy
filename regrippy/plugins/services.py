from enum import Enum

from regrippy import BasePlugin, PluginResult, mactime


class Plugin(BasePlugin):
    """Lists all services installed on the system"""

    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(self.get_currentcontrolset_path() + "\\Services")
        if not key:
            return

        for service in key.subkeys():
            values = [x.name() for x in service.values()]

            res = PluginResult(key=service, value=None)
            res.custom = {
                "image_path": service.value("ImagePath").value()
                if "ImagePath" in values
                else "N/A",
                "start_mode": ServiceStartMode(
                    service.value("Start").value() if "Start" in values else -1
                ),
                "description": service.value("Description").value()
                if "Description" in values
                else "N/A",
            }
            yield res

    def display_human(self, result):
        print(result.key_name)
        print(f"\tDescription: {result.custom['description']}")
        print(f"\tImagePath: {result.custom['image_path']}")
        print(f"\tStart: {result.custom['start_mode']}")
        print()

    def display_machine(self, result):
        print(
            mactime(
                name=f"{result.key_name}\tImagePath={result.custom['image_path']}",
                mtime=result.mtime,
            )
        )


class ServiceStartMode(Enum):
    AUTOMATIC = 2
    BOOT = 0
    DISABLED = 4
    MANUAL = 3
    SYSTEM = 1
    UNKNOWN = -1
