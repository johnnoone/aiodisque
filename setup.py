#!/usr/bin/env python

from setuptools import setup
import versioneer

setup(
    name='aiodisque',
    version=versioneer.get_version(),
    install_requires=[
        'hiredis'
    ],
    cmdclass=versioneer.get_cmdclass()
)
