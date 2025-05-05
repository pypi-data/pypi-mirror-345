#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for the ghahreman package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ghahreman",
    version="0.1.0",
    author="Erfan",
    author_email="zelzeleh.19@gmail.com",
    description="A PyVista-based 3D trophy visualization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elmino-19/ghahreman",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyvista>=0.34.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "ghahreman=ghahreman.trophy:main",
        ],
    },
)
