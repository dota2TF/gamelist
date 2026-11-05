@echo off
pushd "%~dp0"
python scripts\create-local-preview.py
if errorlevel 1 (
    echo Preview generation failed. Check the error above.
    pause
    popd
    exit /b 1
)
start "" "local-preview.html"
popd
