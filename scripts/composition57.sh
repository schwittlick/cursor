#!/bin/zsh

# make sure to run this only with an activated venv

echo "setup requirements"
pip install -r ../requirements.txt --quiet
pip install -e .. --quiet

streamlit run ../experiments/composition57.py