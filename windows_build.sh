#!/usr/bin/env bash
set -euo pipefail
# Build Windows exe using PyInstaller. Run this on Windows (PowerShell/CMD) or in CI on windows-latest.
# If run under WSL, ensure PyInstaller and Python target the native Windows Python.

# Determine add-data separator depending on platform
SEP=";"
if [[ "$(uname -s)" == "Darwin" || "$(uname -s)" == "Linux" ]]; then
  SEP=":"
fi

pyinstaller --clean --onefile --windowed \
  --add-data "data${SEP}data" \
  --hidden-import=tkcalendar \
  --name weekly_reporter main.py

echo "Build finished. See dist/ for the exe (on Windows it'll be weekly_reporter.exe)"
