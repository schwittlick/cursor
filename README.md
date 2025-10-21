# Cursor

[![schwittlick](https://circleci.com/gh/schwittlick/cursor.svg?style=shield)](https://app.circleci.com/pipelines/github/schwittlick/cursor)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/schwittlick/cursor.svg?style=flat-square)
[![GitHub license](https://img.shields.io/github/license/schwittlick/cursor.svg?style=flat-square)](https://github.com/schwittlick/cursor/blob/master/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.13.9](https://img.shields.io/badge/python-3.13.9-blue.svg)](https://www.python.org/downloads/release/python-3139/)

setup

    pyenv install 3.13.9
    pyenv virtualenv 3.13.9 cursor
    pyenv activate cursor
    pip install -r requirements.txt
    git submodule update --init

adjust config.ini

    cp config.ini config_local.ini
    # adjust paths to data folder. within data folder we expect "recordings" and "experiments" folder

test

    # linux/osx
    py.test --cov cursor -v
    ruff format --check .
    
    # single test
    pytest tests/test_renderer.py::test_ascii_renderer

    # windows
    python -m pytest --cov=cursor . -v

recorder

    # check scripts folder
    pip install -e .
    cursor_recorder

experiment

    pip install -e .
    cd experiments
    python file.py

tools

See [tools](tools/README.md) for more information on available tools.

data handling

    # remove recording files with <3kb in file size
    cd data/recordings
    find . -name "*.json" -type 'f' -size -3k -delete
    
    # share dir in local network via sshfs
    sshfs marcel@plot470s.local:/home/marcel/share/ ./share