#!/bin/bash
# remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

mkdir -p build
rm -rf build/PZ_BlenderToolkit.zip
cd src
zip -r ../build/PZ_BlenderToolkit.zip .
