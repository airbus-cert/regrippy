#!/usr/bin/env python3

import os
import sys

import pkg_resources

RST_TEMPLATE = """
Plugin test coverage
====================

Here is a recap of which plugins are properly tested, and which are not. Ideally, we should
strive for 100% coverage :-)

To make this dream a reality, please attach a test file to your pull requests! This way, the 
percentage at least won't go down.

**Current percentage: {percent}%**

.. csv-table:: 
   :header: "Plugin name","Test status"

{table}
"""

PLUGINS_DIR = os.path.join("regrippy", "plugins")
TESTS_DIR = "tests"

if __name__ == "__main__":
    all_plugins = [
        f for f in os.listdir(PLUGINS_DIR) if f.endswith(".py") and f != "__init__.py"
    ]
    all_tests = [
        f for f in os.listdir(TESTS_DIR) if f.startswith("test_") and f.endswith(".py")
    ]

    total = len(all_plugins)
    tested = 0

    if len(sys.argv) == 2 and sys.argv[1] == "--badge":
        for plugin in all_plugins:
            test_name = "test_" + plugin
            if os.path.isfile(os.path.join(TESTS_DIR, test_name)):
                tested += 1

        ratio = tested / total
        color = "red"
        if ratio > 0.3:
            color = "orange"
        if ratio > 0.7:
            color = "green"
        if ratio == 1.0:
            color = "brightgreen"

        url = f"https://img.shields.io/badge/tests-{tested}%2F{total}-{color}.svg"
        print(url)

    else:
        table_rows = []

        for plugin in all_plugins:
            test_name = "test_" + plugin
            row = '   "' + plugin[: -len(".py")] + '",'
            if os.path.isfile(os.path.join(TESTS_DIR, test_name)):
                row += "OK"
                tested += 1
            else:
                row += "MISSING"

            table_rows.append(row)

        print(
            RST_TEMPLATE.format(
                table="\n".join(table_rows), percent=int((tested / total) * 100)
            )
        )
