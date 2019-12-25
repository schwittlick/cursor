#!/bin/zsh

source ./venv/bin/activate
python setup.py install

echo "Running cursor.."
cursor
echo ".. Done"