#!/usr/bin/env python
from setuptools import setup
import pathlib

requires = []

here = pathlib.Path(__file__).parent
with open(here / 'requirements.txt', 'r') as f:
    for line in f:
        print(line)
    requires = [line.strip() for line in f]

print(requires)
try:
    import pypandoc

    long_description = pypandoc.convert("README.md", "rst")
except (IOError, ImportError):
    long_description = ""

packages = [
    "cursor",
]

extras_require = {}

setup(
    name="cursor",
    version="241031",
    description="cursor line experiments",
    long_description=long_description,
    author="Marcel Schwittlick",
    author_email="info@schwittlick.net",
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "cursor_recorder = cursor.recorder:main",
            "discovery = cursor.tools.discovery:discover",
            "sendhpgl = cursor.tools.sendhpgl:main",
            "braille_convert = cursor.tools.braille_converter:main",
        ]
    },
    license="MIT",
    url="https://github.com/schwittlick/cursor",
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10.11",
    ],
)
