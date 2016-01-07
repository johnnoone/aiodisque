#!/usr/bin/env python

from setuptools import setup
import versioneer

setup(
    name='aiodisque',
    version=versioneer.get_version(),
    install_requires=[
        'hiredis'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords=['message broker'],
    url='https://lab.errorist.xyz/aio/aiodisque',
    license='MIT',
    cmdclass=versioneer.get_cmdclass()
)
