Using RegRippy for Incident Response
====================================

RegRippy's focus is ease-of-use during incident response scenarios. Its goal is to get out of 
of the way as much as possible, and to provide you with the answers you need right away whenever
possible.

To this end, you don't need a lot to start using it:

* You'll need a **Windows Registry hive** to work on. A mounted disk dump is ideal, but RegRippy can
  also work on a single isolated hive file.
* You will have to choose **which plugin** you want to run. Depending on the plugin, the hive you
  need can be different.

===================
Choosing the plugin
===================

You can get a look at every plugin available in RegRippy by running:

.. code-block:: shell

   $ regrip.py -l

The plugin are presented, one per line, in the following fashion:

.. code-block:: shell

   - plugin_name (hive): description

The ``plugin_name`` is what you will be using to call this plugin's services. The ``hive`` is the 
type of Registry hive the plugin expects in input. Finally, the ``description`` gives you a 
one-line description of what this plugin does.

Calling the plugin can be done in one of two ways:

.. code-block:: shell
   
   $ regrip.py [options] plugin_name
   $ reg_pluginname [options]

==================
Selecting the hive
==================

Before the plugin can do its magic, you need to specify where your hive file(s) is located.
There are three ways you can do this (and they will be checked in this order):

1. By directly specifying the path to the hive file. You can use the special path "`-`" which
   means "read from `stdin`".

  .. code-block:: shell
     
     --system (or -y) /path/to/SYSTEM
     --software (or -o) /path/to/SOFTWARE
     --sam (or -a) /path/to/SAM
     --ntuser (or -n) /path/to/NTUSER.DAT
     --usrclass (or -u) /path/to/UsrClass.DAT

2. By specifying the path to the folder where ``C:`` is mounted. RegRippy will automatically
   fetch the correct hive(s), provided they are in the right spot. **This is the easiest way to 
   use RegRippy**

  .. code-block:: shell
     
     --root (or -r) /path/to/C

3. By creating environment variable which contain the path to each hive:

  .. code-block:: shell

     export REG_SYSTEM=/path/to/SYSTEM
     export REG_SOFTWARE=/path/to/SOFTWARE
     export REG_SAM=/path/to/SAM
     export REG_NTUSER=/path/to/NTUSER.DAT
     export REG_USRCLASS=/path/to/UsrClass.DAT

4. If analysing a Windows Vista or later system, you can also add the ``--backups`` flag to
   automatically apply the plugin to
   `registry backups <https://www.fireeye.com/blog/threat-research/2019/01/digging-up-the-past-windows-registry-forensics-revisited.html>`_.
   RegRippy will look into the following folders for backup hives:

  .. code-block::

    C:\Windows\System32\config\RegBack\
    %USERPROFILE%\NTUSER.DAT.OLD
    %USERPROFILE%\AppData\Local\Microsoft\Windows\UsrClass.dat.old

==============
Usage examples
==============

Quick findings: get the name of the computer you're analysing

.. code-block:: shell
   
   $ mount /dev/sdb1 /mnt/c
   $ reg_compname --root /mnt/c
   DESKTOP_ABCEDF

Quick findings: extract all programs running at startup, both computer-wide (`SOFTWARE` hive)
and per-user (`NTUSER.DAT` hive)

.. code-block:: shell

   $ reg_run --root /mnt/c --all-user-hives
   # You can add the -v (--verbose) flag to enable more logging, and get the user's name
   # when something is found in NTUSER
