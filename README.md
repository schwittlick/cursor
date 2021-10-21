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

###Plotter handling

hard limits of the plotting area as measured by the machine, in plotter steps

    OH;
    >> -15819, -9298, 15819, 9298
    >> 1mm = 40 steps
    >> your width is 15819 + 15819 / 40 = 790mm
    >> do the same with the height
    
    the plotter drawing are will have +25mm offset at the bottom
    
inkscape

    create document with  that dimensions
    bottom (right) side has 25mm offset
    in order to have everwhere the same offset (30mm) add 25mm offset left, right and top in inkscape
    
    you can use the inkscape plot function.
    serial flow: Hardware RTS/CTS
    center zero point (on big hp plotter)
    change pen speed, default is full speed
    plot featuer: everything off (overcut: 0mm; offset correction: 0mm; precut and autoalign off)


##### HP7595A
    - serial cable with usb adapter
    - ohne nullmodem
    - sendhpgl port file
    - inkscape hpgl export check "centerd"

##### HP7475A
    - serial cable with usb adapter
    - mit nullmodem
    - sendhpgl port file
    - https://github.com/b4ckspace/hpgl-plot

##### HP7475A buffer overflow
    - serial cable with usb adapter
    - mit null modem
    - cat file to port

#### HP7475A inkscape
    - document layout: A3 in landscape 
    - export hpgl not centered

#### HP7475a GPIB HPIB
    https://pearl-hifi.com/06_Lit_Archive/15_Mfrs_Publications/20_HP_Agilent/HP_7475A_Plotter/HP_7475A_Op_Interconnect.pdf
    - Prologix GPIB Configurator
    - Auf ID 5
    - Arduino Serial Monitor, "help++"
    http://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf

##### Roland DPX3300
usb to parallel port adapter

    chmod 777 /dev/usb/lp0
    cat file.hpgl /dev/usb/lp0
