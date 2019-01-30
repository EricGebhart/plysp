#!/usr/bin/env python

# python 3 is required.
from os.path import exists
try:
    # Use setup() from setuptools(/distribute) if available
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from plysp import __version__

setup(
    name='plysp',
    version=__version__,
    # Your name & email here
    author='Eric Gebhart',
    author_email='e.a.gebhart@gmail.com',

    packages=['plysp'],

    scripts=[],
    url='https://github.com/EricGebhart/plysp',
    license='',
    description='A lisp with clojure syntax implemented in Python/Cython',
    long_description=open('README').read() if exists("README") else "",
    entry_points=dict(console_scripts=['plysp=plysp.repl:main']),
    install_requires=[
        'ply>=3.4',
        'funktown>=0.4.6'
    ],
)
