#!/bin/bash

# Get Golang Dependencies
go get github.com/mgutz/ansi
go get golang.org/x/net/html

# Makes directory for dependencies and executable to be installed
mkdir -p tmp_build 
mkdir -p tmp_dist

pip install pyinstaller 

# Creates executable file and sends dependences to the recently created directories
pyinstaller --onefile --workpath ./tmp_build --distpath ./tmp_dist torBot.py

# Puts the executable in the current directory
mv tmp_dist/torBot . 

# Removes both directories and unneeded file
rm -r tmp_build tmp_dist
rm torBot.spec
