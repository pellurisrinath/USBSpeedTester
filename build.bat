@echo off
echo ===================================================
echo Building Standalone USB Speed Test & Monitor App
echo ===================================================
echo.
echo Installing requirements...
pip install pywebview psutil pystray plyer Pillow pyinstaller
echo.
echo Compiling application with PyInstaller...
pyinstaller --noconsole --onefile --add-data "gui;gui" main.py
echo.
echo Done! Standalone executable is available under the 'dist' directory.
echo.
pause
