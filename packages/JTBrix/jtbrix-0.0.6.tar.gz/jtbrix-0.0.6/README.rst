JTBrix
======

.. image:: https://img.shields.io/pypi/v/JTBrix.svg
    :target: https://pypi.python.org/pypi/JTBrix

.. image:: https://img.shields.io/travis/amidn/JTBrix.svg
    :target: https://travis-ci.com/amidn/JTBrix

.. image:: https://readthedocs.org/projects/JTBrix/badge/?version=latest
    :target: https://JTBrix.readthedocs.io/en/latest/?version=latest
    :alt: Documentation Status

JTBrix is a modular Python package for running customizable video-based behavioral experiments in psychology and cognitive science.  
It supports full-screen playback, flexible configuration via YAML, conditional logic flows, and detailed logging of user responses and timing.

* Free software: MIT license
* Documentation: https://JTBrix.readthedocs.io

Features
--------

* Dynamically configurable experiments using a `config.yml` file.
* Supports multiple step types: consent, video, question, popup, dropdown, and end screens.
* Records answers and reaction times per screen.
* Fullscreen iframe-based flow in a single browser tab.
* Video and image stimuli loaded from a customizable static directory.
* Modular design for extension and easy deployment via Flask.

Installation
------------

You can install JTBrix via pip:

.. code-block:: bash

    pip install JTBrix

Usage
-----

Basic example of how to start an experiment:

.. code-block:: python

    from JTBrix import run_test
    result = run_test("path/to/config.yml", "path/to/static/")

By default, JTBrix looks for a configuration file (`config.yml`) and a `static/` folder under the `Data/` directory.

The `static/` folder must include two subfolders:

- `videos/` – for video stimuli (e.g., `.mp4` files)  
- `images/` – for images used in questions (e.g., `.jpeg`, `.png`)

You can place these folders anywhere locally or on a server and provide the paths explicitly when calling `run_test()`.

Credits
-------

JTBrix was designed and developed by Amid Nayerhoda for experimental research in cognitive science and psychology.
