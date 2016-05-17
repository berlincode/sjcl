#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('CHANGES.txt').read().replace('.. :changelog:', '')

setup(
    name='sjcl',
    version='0.1.4',
    description="""
Decrypt and encrypt messages compatible to the "Stanford Javascript Crypto
Library (SJCL)" message format.

This module was created while programming and testing the encrypted
blog platform on cryptedblog.com which is based on sjcl.
""",
    long_description=readme + '\n\n' + history,
    author='Ulf Bartel',
    author_email='elastic.code@gmail.com',
    url='https://github.com/berlincode/sjcl',
    packages=[
        'sjcl',
    ],
    package_dir={'sjcl': 'sjcl'},
    include_package_data=True,
    install_requires=['pycrypto'], # TODO add version >=
    license="LICENSE.txt",
    zip_safe=False,
    keywords='SJCL, AES, encyption, pycrypto, Javascript',
    entry_points={
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
