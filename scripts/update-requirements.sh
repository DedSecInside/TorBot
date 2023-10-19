#! /bin/bash

echo "Writing requirements.txt..."
poetry export --without-hashes --format=requirements.txt > requirements.txt
echo "requirements.txt updated..."
