# regrippy -- a modern Python 3 alternative to RegRipper

## Description

RegRip**py** is an alternative to [RegRipper](https://github.com/keydet89/RegRipper2.8) developed in modern Python 3. It makes use of William Ballenthin's [python-registry](https://github.com/williballenthin/python-registry) to access raw registry hives.

By default, the script will look for the various hives by reading the `REG_SYSTEM`, `REG_SOFTWARE`, `REG_SAM`, `REG_NTUSER` and `REG_USRCLASS` environment variables. This allows the analyst to simply `export` these in their current shell session and not have to worry about specifying them every time they invoke the script.

All plugins should also support both a human-readable and machine-readable output, allowing easy piping to `mactime` or other tools.

## Usage

```
usage: regrip.py [-h] [--system SYSTEM] [--software SOFTWARE] [--sam SAM]
                 [--ntuser NTUSER] [--usrclass USRCLASS] [--root ROOT]
                 [--verbose] [--pipe] [--list]
                 plugin_name

Extract information from Windows Registry hives

positional arguments:
  plugin_name           Name of the plugin to run

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -y SYSTEM
                        Path to the SYSTEM hive. Overrides --root and the
                        REG_SYSTEM environment variable
  --software SOFTWARE, -o SOFTWARE
                        Path to the SOFTWARE hive. Overrides --root and the
                        REG_SOFTWARE environment variable
  --sam SAM, -a SAM     Path to the SAM hive. Overrides --root and the REG_SAM
                        environment variable
  --ntuser NTUSER, -n NTUSER
                        Path to the NTUSER.DAT hive. Overrides the REG_NTUSER
                        environment variable
  --usrclass USRCLASS, -u USRCLASS
                        Path to the UsrClass.DAT hive. Overrides the
                        REG_USRCLASS environment variable
  --root ROOT, -r ROOT  Path to the root 'config' folder.
  --verbose, -v         Be more verbose
  --pipe, -p            Output in a format more suitable to automation
  --list, -l            List available plugins
```

## Development

Creating a plugin is as easy as adding a Python file to the `plugins/` folder. Each plugin must contain:
* A `__REGHIVE__` constant specifying the type of registry hive the plugin works on
  * It can be `SYSTEM`, `SOFTWARE`, `SAM`, `UsrClass.dat` or `NTUSER.DAT`
* A `__DESCRIPTION__` constant providing a one-line description of what the plugin does
* A `run(reg, pipe, logger)` function taking 3 parameters:
  * `reg` will be a `Registry` object (see [python-registry](https://github.com/williballenthin/python-registry))
  * `pipe` is a boolean specifying whether the output will be read by a machine. Mactime format is encouraged when outputting machine-readable information.
    * A `mactime(md5, name, inode, mode_as_string, uid, gid, size, atime, mtime, ctime, btime)` function is available. It will format the parameters in bodyfile format. Note that every parameter is optional.
  * `logger` is a logger which must be used to log errors or warnings

