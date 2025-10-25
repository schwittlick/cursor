# Cursor

[![schwittlick](https://circleci.com/gh/schwittlick/cursor.svg?style=shield)](https://app.circleci.com/pipelines/github/schwittlick/cursor)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/schwittlick/cursor.svg?style=flat-square)
[![GitHub license](https://img.shields.io/github/license/schwittlick/cursor.svg?style=flat-square)](https://github.com/schwittlick/cursor/blob/master/LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.14.0](https://img.shields.io/badge/python-3.14.0-blue.svg)](https://www.python.org/downloads/release/python-3140/)

## Overview

Cursor is a Python project for recording, analyzing, and experimenting with cursor/mouse movement data. It provides tools for capturing mouse interactions, processing recordings, and running experiments on cursor behavior patterns.

## Table of Contents

- [Cursor](#cursor)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Configuration](#configuration)
  - [Testing](#testing)
  - [Running](#running)
    - [Recorder](#recorder)
    - [Experiments](#experiments)
  - [Tools](#tools)
  - [Data Handling](#data-handling)
    - [Remove small recording files](#remove-small-recording-files)
    - [Share directory over local network](#share-directory-over-local-network)
  - [Troubleshooting](#troubleshooting)
    - [Import errors on Linux/macOS](#import-errors-on-linuxmacos)
    - [Virtual environment issues](#virtual-environment-issues)
    - [Test failures on Windows](#test-failures-on-windows)

## Prerequisites

- Python 3.14
- pip and virtualenv (or pyenv)
- System dependencies:
  - PyQt5
  - libcairo2-dev
  - pkg-config
  - python3-dev
  - python3-tk

## Setup

Using uv for setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update

uv python install 3.14
uv venv --python 3.14

source .venv/bin/activate

uv pip install -r requirements.txt
uv pip install -e .

git submodule update --init
```

## Configuration

Copy and customize the configuration file for your environment:

```bash
cp config.ini config_local.ini
# Adjust paths to data folder. Within data folder, we expect "recordings" and "experiments" folders
```

## Testing

Run tests with code coverage and linting:

```bash
# Linux/macOS
py.test --cov cursor -v
ruff format --check .

# Run a single test
pytest tests/test_renderer.py::test_ascii_renderer

# Windows
python -m pytest --cov=cursor . -v
```

## Running

### Recorder

Record cursor movements:

```bash
pip install -e .
cursor_recorder
```

### Experiments

Run experiments on cursor data:

```bash
pip install -e .
cd experiments
python file.py
```

## Tools

See [tools](tools/README.md) for more information on available tools.

## Data Handling

### Remove small recording files

Remove recording files smaller than 3KB:

```bash
cd data/recordings
find . -name "*.json" -type 'f' -size -3k -delete
```

### Share directory over local network

Share a directory via SSHFS:

```bash
sshfs marcel@plot470s.local:/home/marcel/share/ ./share
```

## Troubleshooting

### Import errors on Linux/macOS

If you encounter PyQt5 import errors, ensure system dependencies are installed:

```bash
# macOS
brew install pyqt5

# Ubuntu/Debian
sudo apt install python3-pyqt5 libcairo2-dev pkg-config python3-dev python3-tk
```

### Virtual environment issues

If you encounter permission or environment conflicts, ensure you're using the correct virtual environment:

```bash
pyenv activate cursor
which python  # Should point to your virtualenv
```

### Test failures on Windows

Make sure to use `python -m pytest` on Windows instead of `py.test` directly.
