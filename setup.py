#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

setup(
    name='aiodisque',
    version=versioneer.get_version(),
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    description='Asyncio Disque client',
    packages=find_packages(),
    install_requires=[
        'hiredis'
    ],
    extras_require={
        'curio': ['curio'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords=[
        'infrastructure',
        'message broker',
        'asyncio'
    ],
    url='https://lab.errorist.xyz/aio/aiodisque',
    license='MIT',
    cmdclass=versioneer.get_cmdclass()
)
