#!/bin/bash

rm -rf ./env
mkdir -p ./env
cd ./env
pixi init .
pixi add python spiceypy json5 numpy hatch
pixi shell

cd ..

hatch build


# refs:
#
# https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html