from regrippy import BasePlugin, PluginResult, mactime
from Registry import Registry


class Plugin(BasePlugin):
    """Lists all services installed on the system"""
    __REGHIVE__ = "SYSTEM"

    def run(self):
        key = self.open_key(self.get_currentcontrolset_path() + "\\Services")
        if not key:
            return
        
        for service in key.subkeys():
            try:
                image_path = service.value("ImagePath").value()
            except Registry.RegistryValueNotFoundException:
                image_path = "N/A"
            
            res = PluginResult(key=service, value=None)
            res.custom["image_path"] = image_path
            yield res
    
    def display_human(self, result):
        print(result.key_name, "//", result.custom["image_path"])
    
    def display_machine(self, result):
        print(mactime(name=f"{result.key_name}\tImagePath={result.custom['image_path']}", mtime=result.mtime))
