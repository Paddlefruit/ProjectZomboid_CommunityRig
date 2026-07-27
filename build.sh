#!/bin/bash
mkdir -p build
rm -rf build/PZ_BlenderToolkit.zip
cd src
zip -r ../build/PZ_BlenderToolkit.zip .
