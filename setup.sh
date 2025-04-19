#!/bin/bash

if [ ! -d "./emsdk" ]; then
    echo "Installing emsdk"
    git clone https://github.com/emscripten-core/emsdk.git --branch 1.39.20
    ./emsdk/emsdk install 1.39.20-fastcomp
    ./emsdk/emsdk activate 1.39.20-fastcomp
fi

pip install pdfrw
mkdir build

echo "Run the following command to add emcc:"
echo "source ./emsdk/emsdk_env.sh"