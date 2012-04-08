=================
opencorpora-tools
=================

This package provides Python interface to http://opencorpora.org/

Installation
============

::

    pip install opencorpora-tools

If you have python < 2.7 then argparse and ordereddict packages are required::

    pip install argparse
    pip install ordereddict

Usage
=====

TODO

Development
===========

Development happens at github and bitbucket:

* https://github.com/kmike/opencorpora-tools
* https://bitbucket.org/kmike/opencorpora-tools

The main issue tracker is at github.

Feel free to submit ideas, bugs, pull requests (git or hg) or regular patches.

Running tests
-------------

Make sure `tox <http://tox.testrun.org>`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under python 2.6..3.2 and pypy > 1.8.