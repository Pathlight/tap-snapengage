#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-snapengage",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_snapengage"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    tap-snapengage=tap_snapengage:main
    """,
    packages=["tap_snapengage"],
    package_data = {
        "schemas": ["tap_snapengage/schemas/*.json"]
    },
    include_package_data=True,
)
