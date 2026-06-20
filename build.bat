@echo off
echo ===================================================
echo Building Standalone USB Speed Test & Monitor App
echo ===================================================
echo.
echo Installing requirements...
pip install pywebview psutil pystray plyer Pillow pyinstaller
echo.
echo Compiling application with PyInstaller...
pyinstaller USBSpeedTest.spec
echo.
echo Compiling setup installer (UBSSpeedtest_setup.exe)...
pyinstaller --onefile --noconsole --name UBSSpeedtest_setup --add-data "dist/USBSpeedTest.exe;." --distpath dist src/setup_installer.py
echo.
echo Done! Standalone executable and setup installer are available under the 'dist' directory.
echo.
