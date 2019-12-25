#!/usr/bin/env python
from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = ""

packages = [
    "cursor",
]

requires = []
extras_require = {
}

setup(
    name='cursor',
    version="0.1.1",
    description="cursor line handling",
    long_description=long_description,
    author="Marcel Schwittlick",
    author_email='info@schwittlick.net',
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['cursor = cursor.recorder:runRecorder']
    },
    license='MIT',
    url='https://github.com/schwittlick/cursor',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
)