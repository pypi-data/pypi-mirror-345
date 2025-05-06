libtidy
=======

Python binding for the *libtidy* C library.

Overview
========

| Python |package_bold| module is a low-level binding for *libtidy* C library.
| It is an effort to allow python programs full access to the API implemented and
  provided by the well known `*libtidy* <https://www.html-tidy.org/developer/>`__
  library.

`PyPI record`_.

`Documentation`_.

| |package_bold| is a lightweight Python package, based on the *ctypes* library.
| It is fully compliant implementation of the original C *libtidy* API
  by implementing whole its functionality in a clean Python instead of C.
|
| *libtidy* API documentation can be found at:

  `libtidy API Reference <https://api.html-tidy.org/tidy/tidylib_api_next/>`__

|package_bold| uses the underlying *libtidy* C shared library as specified in
libtidy.cfg (included libtidy-X.X.* is the default), but there is also ability
to specify it programmatically by one of the following ways:

.. code:: python

  import libtidy
  libtidy.config(LIBTIDY="libtidy C shared library absolute path")
  # or
  libtidy.config(LIBTIDY=None)  # included libtidy-X.X.* will be used

About original libtidy:
-----------------------

Borrowed from the `original website <https://www.html-tidy.org/developer/>`__:

**libtidy Introduction**

libtidy is the library version of `HTML Tidy <https://www.html-tidy.org/>`__.
In fact, Tidy is libtidy; the console application is a very simple C application
that links against libtidy. It's what powers Tidy, mod-tidy, and countless other
applications that perform tidying.

**Design factors**

libtidy is Thread Safe and Re-entrant. Because there are many uses for HTML
Tidy - from content validation, content scraping, conversion to XHTML -
it was important to make libtidy run reasonably well within server applications
as well as client side.

Requirements
============

- | It is a fully independent package.
  | All necessary things are installed during the normal installation process.
- ATTENTION: currently works and tested only for Windows.

Installation
============

Prerequisites:

+ Python 3.10 or higher

  * https://www.python.org/
  * with C libtidy 5.9.14 is a primary test environment.

+ pip and setuptools

  * https://pypi.org/project/pip/
  * https://pypi.org/project/setuptools/

To install run:

  .. parsed-literal::

    python -m pip install --upgrade |package|

Development
===========

Prerequisites:

+ Development is strictly based on *tox*. To install it run::

    python -m pip install --upgrade tox

Visit `Development page`_.

Installation from sources:

clone the sources:

  .. parsed-literal::

    git clone |respository| |package|

and run:

  .. parsed-literal::

    python -m pip install ./|package|

or on development mode:

  .. parsed-literal::

    python -m pip install --editable ./|package|

License
=======

  | |copyright|
  | Licensed under the HTML Tidy License
  | https://spdx.org/licenses/HTMLTIDY.html
  | Please refer to the accompanying LICENSE file.

Authors
=======

* Adam Karpierz <adam@karpierz.net>

.. |package| replace:: libtidy
.. |package_bold| replace:: **libtidy**
.. |copyright| replace:: Copyright (c) 2024-2025 Adam Karpierz
.. |respository| replace:: https://github.com/karpierz/libtidy.git
.. _Development page: https://github.com/karpierz/libtidy
.. _PyPI record: https://pypi.org/project/libtidy/
.. _Documentation: https://libtidy.readthedocs.io/
