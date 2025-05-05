
======
JTBrix
======

.. image:: https://img.shields.io/pypi/v/JTBrix.svg
    :target: https://pypi.python.org/pypi/JTBrix

.. image:: https://img.shields.io/travis/amidn/JTBrix.svg
    :target: https://travis-ci.com/amidn/JTBrix

.. image:: https://readthedocs.org/projects/JTBrix/badge/?version=latest
    :target: https://JTBrix.readthedocs.io/en/latest/?version=latest
    :alt: Documentation Status

JTBrix is a modular Python package for running behavioral experiments in psychology.  
It supports video stimuli, conditional user interaction, and detailed logging of responses and reaction times.

* Free software: MIT license
* Documentation: https://JTBrix.readthedocs.io

Features
--------

* Run customizable behavioral experiments with video-based stimuli.
* Play videos, ask related questions, and apply conditional progression logic.
* Collect participant responses and reaction time data.
* Organize stimuli and questions by category.
* Easily extendable with clean modular structure.

Installation
------------

You can install JTBrix via pip:

.. code-block:: bash

    pip install JTBrix

Usage
-----

Basic example of how to start an experiment:

.. code-block:: python

    from jtbrix.logic.flow import run_experiment
    run_experiment(config_path="configs/default.yaml")

(Full usage examples and config format are in the documentation.)

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage





