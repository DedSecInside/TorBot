#!/bin/bash

# Makes directory for dependencies and executable to be installed
mkdir -p tmp_build
mkdir -p tmp_dist

# attempt to install pyinstaller using pip, python3 is prioritized
if command -v pip3 &> /dev/null; then
        pip3 install pyinstaller
elif command -v pip &> /dev/null; then
        pip install pyinstaller
else
        echo "pip is required for installation."
        exit 1
fi


# Creates executable file and sends dependences to the recently created directories
pyinstaller --onefile --workpath ./tmp_build --distpath ./tmp_dist --paths=src src/torBot.py

# Puts the executable in the current directory
mv tmp_dist/torBot .

# Removes both directories and unneeded file
rm -r tmp_build tmp_dist
rm torBot.spec
