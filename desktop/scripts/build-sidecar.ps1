# Freeze the Snapmaker Studio engine sidecar into a single Windows .exe and
# stage it for Tauri's externalBin (target-triple-suffixed name).
#
# Requires: Python with the backend installed (pip install -e backend) plus
# pyinstaller + lxml (pip install -r backend/requirements-build.txt).
#
# Usage (from anywhere):  desktop/scripts/build-sidecar.ps1
$ErrorActionPreference = "Stop"

$backend = (Resolve-Path "$PSScriptRoot\..\..\backend").Path
$triple  = "x86_64-pc-windows-msvc"
$name    = "snapstudio-api-$triple"

Write-Host "Freezing sidecar from $backend ..."
Push-Location $backend
try {
    # --collect-data snapstudio_core : bundle data/*.json loaded via importlib.resources
    # --collect-submodules lxml      : ensure the lxml C-extension parts are included
    pyinstaller --noconfirm --clean --onefile --name $name `
        --collect-data snapstudio_core `
        --collect-submodules lxml `
        sidecar_main.py
} finally {
    Pop-Location
}

$src = Join-Path $backend "dist\$name.exe"
if (-not (Test-Path $src)) { throw "PyInstaller did not produce $src" }

$dstDir = Join-Path $PSScriptRoot "..\src-tauri\bin"
New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
$dst = Join-Path $dstDir "$name.exe"
Copy-Item $src $dst -Force

Write-Host "Sidecar staged -> $dst"
