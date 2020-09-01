import pkg_resources
from Registry.Registry import (RegBigEndian, RegBin, RegDWord, RegExpandSZ,
                               RegFullResourceDescriptor,
                               RegistryKeyNotFoundException,
                               RegistryValueNotFoundException, RegLink,
                               RegMultiSZ, RegNone, RegQWord, RegResourceList,
                               RegResourceRequirementsList, RegSZ)


class LoggerMock(object):
    def __init__(self):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class TimestampMock(object):
    def __init__(self, t=1.5):
        self._t = t
        pass

    def timestamp(self):
        return self._t


class RegistryMock(object):
    def __init__(self, hive_name, hive_type, root):
        self._hive_name = hive_name
        self._hive_type = hive_type
        self._root = root

    def hive_name(self):
        return self._hive_name

    def hive_type(self):
        return self._hive_type

    def root(self):
        return self._root

    def open(self, path):
        return self.root().open(path)

    def set_ccs(self, num):
        select_key = RegistryKeyMock("Select", self.root())
        self.root().add_child(select_key)

        current_value = RegistryValueMock("Current", num, RegDWord)
        select_key.add_value(current_value)

    def dump(self):
        print("🌲")
        for subkey in self.root().subkeys():
            subkey.dump(1)


class RegistryKeyMock(object):
    def __init__(self, name, parent):
        self._name = name
        self._subkeys = []
        self._values = []
        self._parent = parent

    def build(path):
        before, _, last = path.rpartition("\\")
        if not before:
            # We're the root key
            root = RegistryKeyMock("ROOT", None)
            k = RegistryKeyMock(path, root)
            root.add_child(k)
            return k

        parent = RegistryKeyMock.build(before)
        k = RegistryKeyMock(last, parent)
        parent.add_child(k)
        return k

    def open(self, path):
        before, _, after = path.partition("\\")
        if not before:
            return self

        for subkey in self.subkeys():
            if subkey.name().lower() == before.lower():
                return subkey.open(after)

        raise RegistryKeyNotFoundException("Not found: " + path)

    def add_child(self, k):
        self._subkeys.append(k)

    def add_value(self, v):
        self._values.append(v)

    def subkeys(self):
        return self._subkeys

    def values(self):
        return self._values

    def name(self):
        return self._name

    def value(self, name):
        for v in self.values():
            if v.name().lower() == name.lower():
                return v
        raise RegistryValueNotFoundException("Could not find " + name)

    def subkey(self, name):
        for s in self.subkeys():
            if s.name().lower() == name.lower():
                return s

        raise RegistryKeyNotFoundException("Could not find " + name)

    def path(self):
        if self._parent:
            ppath = self._parent.path()
            return ppath + "\\" + self.name()
        else:
            return "\\" + self.name()

    def timestamp(self):
        return TimestampMock()

    def root(self):
        if self._parent:
            return self._parent.root()
        else:
            return self

    def dump(self, depth=0):
        print("\t" * depth + "📁", self.name())
        for v in self.values():
            v.dump(depth + 1)

        for s in self.subkeys():
            s.dump(depth + 1)


class RegistryValueMock(object):
    def __init__(self, name, data, type):
        self._name = name
        self._data = data
        self._type = type

    def name(self):
        if self._name:
            return self._name
        else:
            return "(default)"

    def value(self):
        return self._data

    def value_type(self):
        return self._type

    def value_type_str(self):
        t = self._type
        if t == RegSZ:
            return "RegSZ"
        elif t == RegExpandSZ:
            return "RegExpandSZ"
        elif t == RegBin:
            return "RegBin"
        elif t == RegDWord:
            return "RegDWord"
        elif t == RegMultiSZ:
            return "RegMultiSZ"
        elif t == RegQWord:
            return "RegQWord"
        elif t == RegNone:
            return "RegNone"
        elif t == RegBigEndian:
            return "RegBigEndian"
        elif t == RegLink:
            return "RegLink"
        elif t == RegResourceList:
            return "RegResourceList"
        elif t == RegFullResourceDescriptor:
            return "RegFullResourceDescriptor"
        elif t == RegResourceRequirementsList:
            return "RegResourceRequirementsList"

    def dump(self, depth=0):
        print("\t" * depth + "🗒️", self.name())
