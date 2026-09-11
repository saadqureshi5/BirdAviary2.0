#!/bin/bash
set -e

cd "$(dirname "$0")/../backend"

if [ -f "../.venv/bin/activate" ]; then
    source "../.venv/bin/activate"
fi

pip install pyinstaller

ARCH=$(uname -m)
OS=$(uname -s)

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        TARGET="aarch64-apple-darwin"
    else
        TARGET="x86_64-apple-darwin"
    fi
else
    if [ "$ARCH" = "aarch64" ]; then
        TARGET="aarch64-unknown-linux-gnu"
    else
        TARGET="x86_64-unknown-linux-gnu"
    fi
fi

BIN_NAME="api-${TARGET}"

pyinstaller --name "${BIN_NAME}" \
            --onefile \
            --hidden-import uvicorn \
            --hidden-import sqlmodel \
            --hidden-import pydantic \
            main.py

mkdir -p ../src-tauri/binaries
cp dist/${BIN_NAME} ../src-tauri/binaries/

echo "Sidecar built successfully for ${TARGET}!"
