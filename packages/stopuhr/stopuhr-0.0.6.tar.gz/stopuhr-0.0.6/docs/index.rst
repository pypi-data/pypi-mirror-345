.. stopuhr documentation master file, created by
   sphinx-quickstart on Thu mar 27 19:28:18 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#########################################
Welcome to stopuhr's documentation!
#########################################

**Version**: |version|

A simple tool for measuring durations in Python.

.. toctree::
   :maxdepth: 1

   Reference <reference/index>
   Examples <auto_examples/index>

Quick Start
===========

Installation
------------

You can install stopuhr via pip:

.. code-block:: bash

    pip install stopuhr

However, `uv` is recommended for installing python packages:

.. code-block:: bash

    uv add stopuhr

Usage
-----

With stopuhr it is convinient to measure durations in Python:

.. code-block:: python

    import time
    from stopuhr import stopwatch

    with stopwatch("My Timer"):
        # Do something
        time.sleep(2)

    >>> My Timer took 2.00s

    @stopwatch("My Timer")
    def my_function():
        # Do something
        time.sleep(2)

    >>> My Timer took 2.00s

This library can much more than that. Visit the reference or example section for more details.
