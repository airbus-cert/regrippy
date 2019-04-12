.. RegRippy documentation master file, created by
   sphinx-quickstart on Mon Feb 25 13:56:05 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RegRippy's documentation!
====================================

RegRippy_ is a Python-3 framework for quickly extracting data from Windows registry hives. 
It is heavily inspired by RegRipper_, and reimplements a lot of its plugins. Its main goal
is to simplify the life of DFIR people by giving quick and to-the-point results, without 
sacrificing automated analysis potential.

One of the main goal is also to make plugin creation accessible to all. We believe Python is
a better choice for this than Perl.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   usage
   testcoverage
   createplugin
   testing
   regrip

.. _RegRippy: https://github.com/airbus-cert/regrippy
.. _RegRipper: https://github.com/keydet89/RegRipper2.8

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
