from regrippy import BasePlugin, PluginResult


class Plugin(BasePlugin):
    """Lists all Office files which had macros enabled"""

    __REGHIVE__ = ["NTUSER.DAT"]

    def run(self):
        k = self.open_key("Software\\Microsoft\\Office")
        if not k:
            return

        # Loop over all versions
        for version in k.subkeys():
            try:
                float(version.name())
            except ValueError:
                continue

            # For each version, look for these programs specifically
            for program in ["Word", "Excel", "PowerPoint"]:
                program_key = self.open_key(
                    f"Software\\Microsoft\\Office\\{version.name()}\\{program}\\Security\\Trusted Documents\\TrustRecords"
                )
                if not program_key:
                    continue

                for value in program_key.values():
                    r = PluginResult(key=program_key, value=value)
                    if value.value().endswith(b"\xff\xff\xff\x7f"):
                        yield r

    def display_human(self, result):
        print(result.value_name)
