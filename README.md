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


test
    
    # linux/osx
    py.test --cov cursor -v
    flake8 --max-line-length=100
    
    # single test
    pytest tests/test_renderer.py::test_ascii_renderer

    # windows
    python -m pytest --cov=cursor . -v

recorder

    # check scripts folder
    pip install -e .
    cursor_recorder
    
data handling

    # remove recording files with <3kb in file size
    cd data/recordings
    find . -name "*.json" -type 'f' -size -3k -delete

axidraw?

    h:
    cd Dropbox\CODE\cursor\venc\Scripts\activate.bat
    cd h:\AxiDraw_API_v253r3
    axicli ..\Dropbox\CODE\cursor\data\svg\pen_sample_book\pen_sample_test_45.svg

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

##### HP7475A
- serial cable with usb adapter
- mit nullmodem
- sendhpgl port file

##### HP7475A buffer overflow
- serial cable with usb adapter
- mit null modem
- cat file to port

##### Roland DPX3300
usb to parallel port adapter

    chmod 777 /dev/usb/lp0
    cat file.hpgl /dev/usb/lp0
