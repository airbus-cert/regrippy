#!/usr/bin/env python3

import os

from setuptools import setup

script_folder = os.path.dirname(os.path.realpath(__file__))


def generate_entry_points():
    """
    Walk through plugins folder to generate entry points
    :return: entry points dictionary
    """
    entry_points = {"plugins": [], "console_scripts": []}

    plugins_folder = os.path.join(script_folder, "regrippy", "plugins")
    for plugin_file in os.listdir(plugins_folder):
        if not plugin_file.endswith(".py") or plugin_file == "__init__.py":
            continue
        plugin_name = plugin_file[:-3]
        print(f"add plugin {plugin_name}")
        entry_points["plugins"].append(
            f"{plugin_name} = regrippy.plugins.{plugin_name}:Plugin"
        )
        entry_points["console_scripts"].append(f"reg_{plugin_name} = regrip:main")

    return entry_points


setup(
    name="regrippy",
    version="2.0.0",
    description="A modern Python-3-based alternative to RegRipper",
    long_description="""RegRip**py** is a framework for reading and extracting useful forensics data from Windows registry hives. It is an alternative to [RegRipper](https://github.com/keydet89/RegRipper2.8) developed in modern Python 3. It makes use of William Ballenthin's [python-registry](https://github.com/williballenthin/python-registry) to access the raw registry hives.

The goal of this project is to provide a framework for quickly and easily developing your own plugins in an incident response scenario.

By default, the script will look for the various hives by reading the `REG_SYSTEM`, `REG_SOFTWARE`, `REG_SAM`, `REG_NTUSER` and `REG_USRCLASS` environment variables. This allows the analyst to simply `export` these in their current shell session and not have to worry about specifying them every time they invoke the script.
Alternatively, you can use the `--root` switch to specify the path to the root of the `C:` drive. RegRippy will automatically look into the right places depending on which hive each plugin needs.

All plugins should also support both a human-readable and machine-readable output (the [Bodyfile](https://wiki.sleuthkit.org/index.php?title=Body_file) format), allowing easy piping to `mactime` or other tools.
    """,
    long_description_content_type="text/markdown",
    author="Airbus CERT",
    author_email="cert@airbus.com",
    url="https://github.com/airbus-cert/regrippy",
    python_requires=">=3.6",
    packages=["regrippy", "regrippy.plugins", "regrippy.thirdparty"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Utilities",
        "Intended Audience :: Information Technology",
    ],
    scripts=["regrip.py"],
    install_requires=["wheel", "python-registry > 1.1.0"],
    entry_points=generate_entry_points(),
)
