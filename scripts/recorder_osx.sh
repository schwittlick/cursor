#!/bin/zsh

echo "setup requirements"
pip install -r ../requirements.txt --quiet
pip install -e .. --quiet

cursor_recorder
