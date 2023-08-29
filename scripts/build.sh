#!/bin/bash

echo "Building distributable..." 
poetry build
echo

echo "Publishing..."
poetry publish
