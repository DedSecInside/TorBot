#!/bin/bash

mkdir -p tmp_build 
mkdir -p tmp_dist

pyinstaller --onefile --workpath ./tmp_build --distpath ./tmp_dist torBot.py

mv tmp_dist/torBot . 

rm -r tmp_build tmp_dist
rm torBot.spec
