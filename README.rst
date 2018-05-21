======================
USB-ISS Python Library
======================

.. image:: https://img.shields.io/pypi/v/usb_iss.svg
    :target: https://pypi.python.org/pypi/usb_iss
    :alt: PyPi

.. image:: https://img.shields.io/travis/sneakypete81/usb_iss.svg
    :target: https://travis-ci.org/sneakypete81/usb_iss
    :alt: TravisCI

.. image:: https://readthedocs.org/projects/usb-iss/badge/?version=latest
    :target: https://usb-iss.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://pyup.io/repos/github/sneakypete81/usb_iss/shield.svg
    :target: https://pyup.io/repos/github/sneakypete81/usb_iss/
    :alt: Updates

Python library for the USB-ISS module.

.. image:: https://www.robot-electronics.co.uk/images/usb-iss-300.png
    :alt: USB ISS Module

**USB ISS module documentation:**
  https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm

**Python API documentation:**
  https://usb-iss.readthedocs.io

Features
--------

* I2C Mode
* IO Mode (untested)
* SPI Mode (not yet implemented)
* Serial Mode (not yet implemented)

Usage Example
-------------
.. code-block:: python

    from usb_iss import UsbIss, defs

    # Configure I2C mode

    iss = UsbIss()
    iss.open("COM3")
    iss.setup_i2c()

    # Write and read back some data

    iss.i2c.write(0xC4, 0, [0, 1, 2]);
    data = iss.i2c.read(0xC4, 0, 3)

    print(data)
    # [0, 1, 2]


----

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
