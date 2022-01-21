#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'pyserial',
    'enum34; python_version=="2.7"',
]

setup(
    author="Pete Burgers",
    author_email='sneakypete81@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python library for the USB-ISS board.",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + changelog,
    include_package_data=True,
    keywords='usb_iss',
    name='usb_iss',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/sneakypete81/usb_iss',
    version='2.0.1',
    zip_safe=False,
)
