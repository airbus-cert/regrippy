# regrippy -- a modern Python 3 alternative to RegRipper

*This is the public GitHub repository of RegRippy*

*We are aware of the existence of [mkorman90/regipy](https://github.com/mkorman90/regipy), which has a similar goal. Both projects were developed in parallel, we were not aware of any other project like RegRippy when we started developing it.*

## Description

RegRip**py** is a framework for reading and extracting useful forensics data from Windows registry hives. It is an alternative to [RegRipper](https://github.com/keydet89/RegRipper2.8) developed in modern Python 3. It makes use of William Ballenthin's [python-registry](https://github.com/williballenthin/python-registry) to access the raw registry hives.

The goal of this project is to provide a framework for quickly and easily developing your own plugins in an incident response scenario.

This tool will try its best to stay out of your way and quickly provide you with usable data:
```
# Get the computer name
$ regrip.py --root /mnt/evidence/C compname
JOHN-DESKTOP

# Get URLs typed in IE for all users on a machine
$ regrip.py -v --root /mnt/evidence/C --all-user-hives typedurls
regrip.py:info:Administrator
regrip.py:warn:Could not open key Software\Microsoft\Internet Explorer\TypedURLs
regrip.py:info:John
https://google.com/?q=how+to+buy+bitcoin
```

All plugins should also support both a human-readable and machine-readable output (the [Bodyfile](https://wiki.sleuthkit.org/index.php?title=Body_file) format), allowing easy piping to `mactime` or other tools.

## Install

RegRippy is available on PyPI and can be installed using `pip`:
```
$ pip install regrippy
```

If you want the bleeding-edge release, it can be installed like any other Python package using `pip` or `setuptools`:
```
$ pip install .
# Alternatively
$ python3 setup.py install
```

Symlinks will automatically be created for all plugins: for example, you can call the `compname`
plugin by running:
```
$ reg_compname -r /mnt/c/
```

## Usage

```
usage: regrip.py [-h] [--system SYSTEM] [--software SOFTWARE] [--sam SAM]
                 [--ntuser NTUSER] [--usrclass USRCLASS] [--root ROOT]
                 [--all-user-hives] [--verbose] [--pipe] [--list]
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
  --root ROOT, -r ROOT  Path to the C: folder.
  --all-user-hives      Work on all NTUSER.DAT and USRCLASS.DAT hives if
                        required. Requires --root. Overrides --ntuser and
                        --usrclass.
  --verbose, -v         Be more verbose
  --pipe, -p            Force output in pipe format
  --list, -l            List available plugins
```

## Documentation & development

If you want to make your own plugin using the RegRippy framework, head over to [the documentation](https://airbus-cert.github.io/regrippy) right now!

You can also build the documentation yourself by running:
```
$ tox -e docs
```

## Testing

This project uses [tox](https://tox.readthedocs.io/en/latest/) to automate the testing process, as well as [pytest](http://pytest.org/) for the test themselves.

Running the tests can be done by invoking:
```
$ tox -e py37
```

## Credits

- This project is under copyright of the [Airbus Computer Emergency Response Team (CERT)](https://www.trusted-introducer.org/directory/teams/ai-cert.html) and distributed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license
- [keydet89](https://github.com/keydet89) for his [RegRipper](https://github.com/keydet89/RegRipper2.8) project which was a great inspiration
- [Willi Ballenthin](http://www.williballenthin.com/) for his [python-registry](https://github.com/williballenthin/python-registry) framework

## License

RegRippy is released under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
