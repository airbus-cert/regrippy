from regrippy import BasePlugin, mactime, PluginResult
from Registry.Registry import (
    RegistryKeyNotFoundException,
    RegistryValueNotFoundException,
)


class Plugin(BasePlugin):
    """Lists information about PuTTY connections: saved public keys, saved sessions, etc."""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        k = self.open_key(r"Software\SimonTatham\PuTTY")
        if not k:
            return

        # SSH host keys
        try:
            ssh_host_keys = k.subkey("SshHostKeys")
            for v in ssh_host_keys.values():
                name = v.name()
                crypto, host = name.split("@")

                r = PluginResult(key=ssh_host_keys, value=v)
                r.custom["type"] = "sshkey"
                r.custom["crypto"] = crypto
                r.custom["host"] = host

                yield r
        except RegistryKeyNotFoundException:
            self.warning("Could not find SshHostKeys subkey")

        # Saved sessions
        try:
            sessions = k.subkey("Sessions")
            for sess in sessions.subkeys():
                try:
                    name = sess.name()
                    host = sess.value("HostName").value()
                    proto = sess.value("Protocol").value()

                    r = PluginResult(key=sess)
                    r.custom["type"] = "session"
                    r.custom["host"] = host
                    r.custom["protocol"] = proto

                    yield r
                except RegistryValueNotFoundException:
                    self.warning(f"Malformed entry: {sess.name()}")
        except RegistryKeyNotFoundException:
            self.warning("Could not find Sessions subkey")

    def display_human(self, res):
        if res.custom["type"] == "sshkey":
            print(f"[SSH KEY] {res.custom['host']}\t(key type: {res.custom['crypto']})")
        elif res.custom["type"] == "session":
            print(
                f"[SESSION] \"{res.key_name}\" => {res.custom['host']}\t(protocol: {res.custom['protocol']})"
            )
        else:
            self.error(f"Unknown result type: {res.custom['type']}")

    def display_machine(self, res):
        if res.custom["type"] == "sshkey":
            print(
                mactime(
                    name=f"PuTTY SSH Key: {res.custom['host']} with {res.custom['crypto']}",
                    mtime=res.mtime,
                )
            )
        elif res.custom["type"] == "session":
            print(
                mactime(
                    name=f"PuTTY Session: {res.custom['host']} with {res.custom['protocol']}",
                    mtime=res.mtime,
                )
            )
