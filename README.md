# Cursor

[![schwittlick](https://circleci.com/gh/schwittlick/cursor.svg?style=shield)](https://app.circleci.com/pipelines/github/schwittlick/cursor) 
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/schwittlick/cursor.svg?style=flat-square) 
[![GitHub license](https://img.shields.io/github/license/schwittlick/cursor.svg?style=flat-square)](https://github.com/schwittlick/cursor/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)

setup

    pyenv install 3.6.8
    pyenv virtualenv 3.6.8 cursor
    pyenv activate cursor
    pip install -r requirements.txt


test
    
    # linux/osx
    py.test --cov cursor
    flake8 --max-line-length=88

    # windows
    cd tests
    python -m pytest --cov=cursor .

recorder

    # check scripts folder
    pip install -e .
    cursor

axidraw?

    h:
    cd Dropbox\CODE\cursor\venc\Scripts\activate.bat
    cd h:\AxiDraw_API_v253r3
    axicli ..\Dropbox\CODE\cursor\data\svg\pen_sample_book\pen_sample_test_45.svg
