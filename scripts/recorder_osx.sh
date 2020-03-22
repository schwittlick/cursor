#!/bin/bash

cd ..
source ./venv/bin/activate
python setup.py install

echo "Running cursor recorder.."
cursor
echo ".. Done"
cd -
