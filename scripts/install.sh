#!/bin/bash

echo "Installing torbot"
echo
python -m pip install torbot
echo
echo "TorBot installed. Run with 'python -m torbot'"
echo

echo "Setting GOPATH to access executable"
export PATH=${PATH}:`go env GOPATH`/bin
echo "New Path ${PATH}"
echo

echo "Installing gotor"
echo
cd gotor/cmd/main
go install gotor.go
echo "Gotor installed. Run with 'gotor'."

cd ../../..
