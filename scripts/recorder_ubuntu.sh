#!/bin/bash

# make sure to run this only with an activated venv

echo "setup requirements"
pip install -r ../requirements.txt --quiet
pip install -e .. --quiet

cursor_recorder
