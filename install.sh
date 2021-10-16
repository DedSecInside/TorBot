#!/bin/bash

# Makes directory for dependencies and executable to be installed
mkdir -p tmp_build
mkdir -p tmp_dist

# attempt to install pyinstaller using pip, python3 is prioritized
if command -v poetry &> /dev/null; then
        poetry install
        poetry update
else
        echo "poetry is required for installation."
        exit 1
fi


# Creates executable file and sends dependences to the recently created directories
pyinstaller --onefile --workpath ./tmp_build --distpath ./tmp_dist --paths=src src/torBot.py

# Puts the executable in the current directory
mv tmp_dist/torBot .

# Removes both directories and unneeded file
rm -r tmp_build tmp_dist
rm torBot.spec
