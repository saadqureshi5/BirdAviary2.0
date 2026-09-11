# build-sidecar.ps1
$ErrorActionPreference = "Stop"

cd "$PSScriptRoot\..\backend"

if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    . "..\.venv\Scripts\Activate.ps1"
}

pip install pyinstaller

pyinstaller --name "api-x86_64-pc-windows-msvc" `
            --onefile `
            --hidden-import uvicorn `
            --hidden-import sqlmodel `
            --hidden-import pydantic `
            main.py

$binaries_dir = "..\src-tauri\binaries"
if (-not (Test-Path $binaries_dir)) {
    New-Item -ItemType Directory -Force -Path $binaries_dir
}

Copy-Item "dist\api-x86_64-pc-windows-msvc.exe" -Destination "$binaries_dir\" -Force

Write-Host "Sidecar built successfully for Windows!"
