#! /bin/bash

echo "Removing torbot as library..."
pip uninstall torbot
echo

echo "Removing torbot as module..."
python -m pip uninstall torbot
