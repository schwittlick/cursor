# Cursor

[![schwittlick](https://circleci.com/gh/schwittlick/cursor.svg?style=shield)](https://app.circleci.com/pipelines/github/schwittlick/cursor) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/schwittlick/cursor)

setup

    pyenv install 3.6.8
    pyenv virtualenv 3.6.8 cursor
    pyenv activate cursor
    pip install -r requirements.txt
    ./install_and_run.sh


test
    
    # linux/osx
    py.test --cov cursor
    flake8 --max-line-length=127

    # windows
    cd tests
    python -m pytest --cov=cursor .


axidraw?

    h:
    cd Dropbox\CODE\cursor\venc\Scripts\activate.bat
    cd h:\AxiDraw_API_v253r3
    axicli ..\Dropbox\CODE\cursor\data\svg\pen_sample_book\pen_sample_test_45.svg
