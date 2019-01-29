#!/usr/bin/env python3

import argparse
import os
import sys
import logging
import types
from importlib.machinery import SourceFileLoader

from Registry import Registry

l = logging.getLogger(__name__)
l.setLevel("ERROR")

def first(*args):
    for arg in args:
        if arg:
            return arg
    return None


def get_hive_path(args, hive_name):
    hives = {
        "system": first(args.system, os.path.join(args.root, "SYSTEM") if args.root else "", os.getenv("REG_SYSTEM")),
        "software": first(args.software, os.path.join(args.root, "SOFTWARE") if args.root else "", os.getenv("REG_SOFTWARE")),
        "sam": first(args.sam, os.path.join(args.root, "SAM") if args.root else "", os.getenv("REG_SAM")),
        "ntuser.dat": first(args.ntuser, os.getenv("REG_NTUSER")),
        "usrclass.dat": first(args.usrclass, os.getenv("REG_USRCLASS"))
    }

    if hive_name.lower() not in hives.keys():
        return None
    return hives[hive_name.lower()]


def mactime(md5="0", name="", inode=0, mode_as_string="", uid=0, gid=0, size=0, atime=0, mtime=0, ctime=0, btime=0):
    return "|".join([md5, name, str(inode), mode_as_string, str(uid), str(gid), str(size), str(atime), str(mtime), str(ctime), str(btime)])


def list_plugins():
    base_folder = os.path.dirname(os.path.abspath(__file__))
    plugins_folder = os.path.join(base_folder, "plugins")
    for plugin_file in os.listdir(plugins_folder):
        if not plugin_file.endswith(".py"):
            continue
        try:
            loader = SourceFileLoader("plugin", os.path.join(plugins_folder, plugin_file))
            plugin = types.ModuleType(loader.name)
            loader.exec_module(plugin)
            print(f"- {plugin_file[:-3]} ({plugin.__REGHIVE__}): {plugin.__DESCRIPTION__}")
        except ImportError as ie:
            print("Could not load plugin:", ie, file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Extract information from Windows Registry hives")

    parser.add_argument("--system", "-y", help="Path to the SYSTEM hive. Overrides --root and the REG_SYSTEM environment variable", type=str, default="")
    parser.add_argument("--software", "-o", help="Path to the SOFTWARE hive. Overrides --root and the REG_SOFTWARE environment variable", type=str, default="")
    parser.add_argument("--sam", "-a", help="Path to the SAM hive. Overrides --root and the REG_SAM environment variable", type=str, default="")
    parser.add_argument("--ntuser", "-n", help="Path to the NTUSER.DAT hive. Overrides the REG_NTUSER environment variable", type=str, default="")
    parser.add_argument("--usrclass", "-u", help="Path to the UsrClass.DAT hive. Overrides the REG_USRCLASS environment variable", type=str, default="")
    parser.add_argument("--root", "-r", help="Path to the root 'config' folder.", type=str, default="")
    parser.add_argument("--verbose", "-v", help="Be more verbose", action="store_true")
    parser.add_argument("--pipe", "-p", help="Output in a format more suitable to automation", action="store_true")
    parser.add_argument("--list", "-l", help="List available plugins", action="store_true")
    parser.add_argument("plugin_name", help="Name of the plugin to run", type=str)

    if "--list" in sys.argv or "-l" in sys.argv:
        list_plugins()
        return

    args = parser.parse_args()

    if args.verbose:
        l.setLevel("DEBUG")

    base_folder = os.path.dirname(os.path.abspath(__file__))
    plugin_path = os.path.join(base_folder, "plugins", args.plugin_name + ".py")

    try:
        loader = SourceFileLoader("plugin", plugin_path)
        plugin = types.ModuleType(loader.name)
        loader.exec_module(plugin)
    except FileNotFoundError:
        print("No such plugin:", args.plugin_name, file=sys.stderr)
        return

    hive_path = get_hive_path(args, plugin.__REGHIVE__)
    if not hive_path:
        print("Required hive was not found:", plugin.__REGHIVE__, file=sys.stderr)
        return

    reg = Registry.Registry(hive_path)
    plugin.mactime = mactime
    plugin.run(reg, args.pipe, l)

if __name__ == "__main__":
    main()