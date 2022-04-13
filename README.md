# Cursor

[![schwittlick](https://circleci.com/gh/schwittlick/cursor.svg?style=shield)](https://app.circleci.com/pipelines/github/schwittlick/cursor) 
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/schwittlick/cursor.svg?style=flat-square) 
[![GitHub license](https://img.shields.io/github/license/schwittlick/cursor.svg?style=flat-square)](https://github.com/schwittlick/cursor/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)

setup

    pyenv install 3.9.0
    pyenv virtualenv 3.9.0 cursor
    pyenv activate cursor
    pip install -r requirements.txt
    git submodule update --init


test
    
    # linux/osx
    py.test --cov cursor -v
    flake8 --max-line-length=100 --ignore=E402,W503
    
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
    
data handling

    # remove recording files with <3kb in file size
    cd data/recordings
    find . -name "*.json" -type 'f' -size -3k -delete

plotters

HP Draftmaster SX/HP7595A,
HP7475A,
Roland DG DXY-980,
Roland DG DXY-990,
Roland DG DXY-885,
Roland DG DXY-1200,
Tektronix 4662,
Aritma 512,
Roland DG DPX3300,
Roland DG CAMM-1 PNC-1000,
A0 DIY

Ink Tips

    1. 1x 2.0mm
    2. 2x 1.4mm 


https://github.com/beardicus/awesome-plotters#manuals-and-ephemera
