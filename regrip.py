#!/usr/bin/env python3

import argparse
import logging
import os
import sys

import pkg_resources
from Registry import Registry

logging.basicConfig()
l = logging.getLogger("regrippy")
l.setLevel("ERROR")


def first(*args):
    for arg in args:
        if arg:
            return arg
    return None


def find_file_nocase(root, file_name):
    for file in os.listdir(root):
        if file.lower() == file_name.lower():
            return file
    return None


def find_path_nocase(root_path, rest_list):
    full_path_parts = []
    for part in rest_list:
        actual_name = find_file_nocase(os.path.join(root_path, *full_path_parts), part)
        if not actual_name:
            return None
        full_path_parts.append(actual_name)

    return os.path.join(root_path, *full_path_parts)


def get_hive_paths(args, hive_name):
    # use REG_ROOT to set root path of hive
    args.root = args.root or os.getenv("REG_ROOT")

    if (
        hive_name.lower() in ["all", "ntuser.dat", "usrclass.dat"]
        and args.all_user_hives
        and not args.root
    ):
        print("Error: --all-user-hives requires --root", file=sys.stderr)
        sys.exit(3)

    # Basic cases
    if hive_name.lower() == "system":
        path = first(
            args.system,
            find_path_nocase(args.root, ["windows", "system32", "config", "system"])
            if args.root
            else None,
            os.getenv("REG_SYSTEM"),
        )
        result = [path] if path else None
        if args.backups and path:
            parent = os.path.dirname(path)
            regback = find_path_nocase(parent, ["regback", "system"])
            if regback:
                result.append(regback)
        return result
    elif hive_name.lower() == "software":
        path = first(
            args.software,
            find_path_nocase(args.root, ["windows", "system32", "config", "software"])
            if args.root
            else None,
            os.getenv("REG_SOFTWARE"),
        )
        result = [path] if path else None
        if args.backups and path:
            parent = os.path.dirname(path)
            regback = find_path_nocase(parent, ["regback", "software"])
            if regback:
                result.append(regback)
        return result
    elif hive_name.lower() == "sam":
        path = first(
            args.sam,
            find_path_nocase(args.root, ["windows", "system32", "config", "sam"])
            if args.root
            else None,
            os.getenv("REG_SAM"),
        )
        result = [path] if path else None
        if args.backups and path:
            parent = os.path.dirname(path)
            regback = find_path_nocase(parent, ["regback", "sam"])
            if regback:
                result.append(regback)
        return result
    elif hive_name.lower() == "ntuser.dat" and not args.all_user_hives:
        path = first(args.ntuser, os.getenv("REG_NTUSER"))
        result = [path] if path else None
        if args.backups and path:
            parent = os.path.dirname(path)
            regback = find_path_nocase(parent, ["ntuser.dat.old"])
            if regback:
                result.append(regback)
        return result
    elif hive_name.lower() == "usrclass.dat" and not args.all_user_hives:
        path = first(args.usrclass, os.getenv("REG_USRCLASS"))
        result = [path] if path else None
        if args.backups and path:
            parent = os.path.dirname(path)
            regback = find_path_nocase(parent, ["usrclass.dat.old"])
            if regback:
                result.append(regback)
        return result

    # All user hives
    elif hive_name.lower() in ["ntuser.dat", "usrclass.dat"] and args.all_user_hives:
        hive_paths = []
        users_folder = find_path_nocase(args.root, ["users"])
        if users_folder is None:
            # Not found, let's try "Documents and Settings"
            users_folder = find_path_nocase(args.root, ["Documents And Settings"])

        if users_folder is None:
            # Still nothing, we didn't find the Users folder, crash&burn
            raise RuntimeError("Could not find the Users folder")

        for user_dir in os.listdir(users_folder):
            current_user_dir = os.path.join(users_folder, user_dir)
            if not os.path.isdir(current_user_dir):
                continue
            if hive_name.lower() == "ntuser.dat":
                path = find_path_nocase(current_user_dir, ["ntuser.dat"])
                if path is not None:
                    hive_paths.append(path)

                    if args.backups:
                        backup = find_path_nocase(current_user_dir, ["ntuser.dat.old"])
                        if backup:
                            hive_paths.append(backup)
            else:
                path = find_path_nocase(
                    current_user_dir,
                    ["appdata", "local", "microsoft", "windows", "usrclass.dat"],
                )
                if path is not None:
                    hive_paths.append(path)

                    if args.backups:
                        backup = find_path_nocase(
                            current_user_dir,
                            [
                                "appdata",
                                "local",
                                "microsoft",
                                "windows",
                                "usrclass.dat.old",
                            ],
                        )
                        if backup:
                            hive_paths.append(backup)

        return hive_paths

    elif hive_name.lower() == "all":
        hive_paths = []
        for hive in ["system", "software", "sam", "ntuser.dat", "usrclass.dat"]:
            paths = get_hive_paths(args, hive)
            if paths:
                hive_paths.extend(paths)
        return hive_paths

    return None


def list_plugins():
    for ep in pkg_resources.iter_entry_points(group="plugins"):
        plugin = ep.load()
        print(f"- {ep.name}({plugin.__REGHIVE__}): {plugin.__doc__}")


def load_plugin(plugin_name):
    for ep in pkg_resources.iter_entry_points(group="plugins"):
        if ep.name == plugin_name:
            return ep.load()

    raise ValueError(f"No such plugin: {plugin_name}")


def main():
    if os.path.basename(sys.argv[0]).lower() != "regrip.py":
        # Issue #5: allow selecting plugins based on argv[0]
        plugin_name = os.path.basename(sys.argv[0])

        # Allow the symlink to be called reg_pluginname to reduce risk of collision
        if plugin_name.startswith("reg_"):
            plugin_name = plugin_name[len("reg_") :]
    else:
        plugin_name = None

    parser = argparse.ArgumentParser(
        description="Extract information from Windows Registry hives"
    )

    parser.add_argument(
        "--system",
        "-y",
        help="Path to the SYSTEM hive. Overrides --root and the REG_SYSTEM environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--software",
        "-o",
        help="Path to the SOFTWARE hive. Overrides --root and the REG_SOFTWARE environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--sam",
        "-a",
        help="Path to the SAM hive. Overrides --root and the REG_SAM environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--ntuser",
        "-n",
        help="Path to the NTUSER.DAT hive. Overrides the REG_NTUSER environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--usrclass",
        "-u",
        help="Path to the UsrClass.DAT hive. Overrides the REG_USRCLASS environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--root",
        "-r",
        help="Path to the C: folder. Overrides the REG_ROOT environment variable",
        type=str,
        default="",
    )
    parser.add_argument(
        "--all-user-hives",
        help="Work on all NTUSER.DAT and USRCLASS.DAT hives if required. Requires --root. Overrides --ntuser and --usrclass.",
        action="store_true",
    )
    parser.add_argument(
        "--backups",
        action="store_true",
        help="Run the plugin on backup registry hives as well (does not work for hives loaded from stdin)",
    )
    parser.add_argument("--verbose", "-v", help="Be more verbose", action="store_true")
    parser.add_argument(
        "--bodyfile", "-b", help="Force output in Bodyfile format", action="store_true"
    )
    parser.add_argument(
        "--list", "-l", help="List available plugins", action="store_true"
    )

    if not plugin_name:
        parser.add_argument("plugin_name", help="Name of the plugin to run", type=str)

    if "--list" in sys.argv or "-l" in sys.argv:
        list_plugins()
        return

    args = parser.parse_args()
    if not plugin_name:
        plugin_name = args.plugin_name

    if args.verbose:
        l.setLevel("DEBUG")

    plugin = load_plugin(plugin_name)

    if type(plugin.__REGHIVE__) == str:
        hive_names = [plugin.__REGHIVE__]
    else:
        hive_names = plugin.__REGHIVE__

    for hive_name in hive_names:
        hive_paths = get_hive_paths(args, hive_name)
        if not hive_paths:
            print("[!] Hive not found:", hive_name, file=sys.stderr)
            continue

        for hive_path in hive_paths:
            if hive_path == "-":
                # Special case: read hive from stdin
                reg = Registry.Registry(sys.stdin.buffer)
            else:
                reg = Registry.Registry(hive_path)

            p = plugin(reg, l, hive_name, hive_path)
            results = list(p.run())

            if results:
                for result in results:
                    if args.bodyfile:
                        p.display_machine(result)
                    else:
                        if hive_name == "NTUSER.DAT":
                            print(f"[.] User: {p.guess_username()}")
                        p.display_human(result)


if __name__ == "__main__":
    main()
