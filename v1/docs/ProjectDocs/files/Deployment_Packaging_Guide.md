# Deployment & Packaging Guide
## USB Speed Test and Monitoring Application

---

## Table of Contents

1. [Build Environment Setup](#build-environment-setup)
2. [PyInstaller Configuration](#pyinstaller-configuration)
3. [Windows Deployment](#windows-deployment)
4. [macOS Deployment](#macos-deployment)
5. [Linux Deployment](#linux-deployment)
6. [Code Signing & Security](#code-signing--security)
7. [Distribution & Release](#distribution--release)
8. [CI/CD Pipeline](#cicd-pipeline)

---

## Build Environment Setup

### Prerequisites

#### All Platforms
```bash
# Install Python 3.9+
python --version  # Should be 3.9 or higher

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Windows-Specific
```bash
# Install NSIS for installer creation
# Download from https://nsis.sourceforge.io/Download

# Install Visual C++ build tools (optional, for some packages)
# Download from Microsoft website

# Install Windows SDK (optional, for code signing)
```

#### macOS-Specific
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python3 create-dmg
```

#### Linux-Specific
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-venv build-essential libfuse2

# CentOS/RHEL
sudo yum install python3-devel gcc g++ make libfuse

# Create AppImage support
wget https://github.com/AppImage/appimagetool/releases/download/13/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

### Python Dependencies

#### requirements.txt
```
pywebview==4.0.3
psutil==5.8.0
Jinja2==3.0.3
pystray==0.17.3
plyer==2.1.0
requests==2.28.0
Pillow==9.0.0
pyinstaller==5.5.0
pyinstaller-hooks-contrib==2022.8
```

#### requirements-dev.txt
```
pytest==7.1.2
pytest-cov==3.0.0
black==22.6.0
flake8==4.0.1
mypy==0.960
```

### Installation Steps

```bash
# Clone or download project
git clone https://github.com/yourorg/usb-speedtest.git
cd usb-speedtest

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Verify installation
python -c "import pywebview; print(pywebview.__version__)"
```

---

## PyInstaller Configuration

### pyinstaller.spec

```python
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for USB Speed Test application
Build command: pyinstaller pyinstaller.spec
"""

import os
import sys
from PyInstaller.utils.hooks import get_module_file_attribute

# Determine platform
IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['src/main.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        ('gui', 'gui'),  # Include GUI files
        ('src/modules', 'modules'),  # Include modules
        ('src/utils', 'utils'),  # Include utilities
    ],
    hiddenimports=[
        'pywebview',
        'psutil',
        'pystray',
        'plyer',
        'Jinja2',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['matplotlib', 'pandas', 'numpy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='USBSpeedTest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if IS_WINDOWS else None,
)

# macOS-specific configuration
if IS_MACOS:
    app = BUNDLE(
        exe,
        name='USBSpeedTest.app',
        icon='assets/icon.icns',
        bundle_identifier='com.usb-speedtest.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'NSRequiresIPhoneOS': False,
            'CFBundleInfoDictionaryVersion': '6.0',
        },
    )

# Linux-specific configuration (AppImage)
if IS_LINUX:
    # Create AppImage structure
    pass
```

---

## Windows Deployment

### Build Steps

```batch
@echo off
REM Build script for Windows

REM Set environment variables
set PYTHON_VERSION=3.9
set ARCH=x64

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Build executable
pyinstaller pyinstaller.spec ^
    --distpath=dist/windows ^
    --buildpath=build ^
    --specpath=build_specs ^
    --upx-dir="%PROGRAMFILES%\UPX"

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

echo Build successful!
```

### NSIS Installer Script (installer.nsi)

```nsis
; NSIS Installer Script for USB Speed Test
; Installation: makensis installer.nsi

!include "MUI2.nsh"

; Variables
!define APP_NAME "USB Speed Test"
!define APP_VERSION "1.0.0"
!define PUBLISHER "Your Organization"
!define APP_EXECUTABLE "USBSpeedTest.exe"
!define DIST_DIR "dist\windows\USBSpeedTest"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer attributes
Name "${APP_NAME} ${APP_VERSION}"
OutFile "dist\USBSpeedTest-${APP_VERSION}-installer.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

; Install section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy executable and dependencies
    File /r "${DIST_DIR}\*.*"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
    
    ; Register uninstaller
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayName" "${APP_NAME} ${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "Publisher" "${PUBLISHER}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Uninstall section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
```

### Build Windows Installer

```bash
# Install NSIS (download from https://nsis.sourceforge.io/Download)

# Build executable
pyinstaller pyinstaller.spec

# Create installer
makensis installer.nsi

# Output: dist/USBSpeedTest-1.0.0-installer.exe
```

---

## macOS Deployment

### Build Steps

```bash
#!/bin/bash
# build_macos.sh - macOS build script

set -e

echo "Building USB Speed Test for macOS..."

# Activate virtual environment
source venv/bin/activate

# Build executable with PyInstaller
pyinstaller pyinstaller.spec \
    --distpath=dist/macos \
    --buildpath=build \
    --specpath=build_specs

# Create DMG installer
create-dmg \
  --volname "USB Speed Test" \
  --volicon "assets/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "USBSpeedTest.app" 100 100 \
  --hide-extension "USBSpeedTest.app" \
  --app-drop-link 400 100 \
  "dist/USBSpeedTest-1.0.0.dmg" \
  "dist/macos/"

echo "macOS build complete!"
echo "Output: dist/USBSpeedTest-1.0.0.dmg"
```

### Code Signing (macOS)

```bash
#!/bin/bash
# sign_macos.sh - Code signing script

APP_PATH="dist/macos/USBSpeedTest.app"
CODESIGN_IDENTITY="Developer ID Application: Your Name"

# Sign the application
codesign --deep --force --verify --verbose \
    --sign "${CODESIGN_IDENTITY}" \
    --timestamp \
    "${APP_PATH}"

# Verify signature
codesign -v "${APP_PATH}"

# Notarize for Big Sur+ (requires Apple Developer account)
xcrun notarytool submit "dist/USBSpeedTest-1.0.0.dmg" \
    --apple-id "your-apple-id@example.com" \
    --password "app-specific-password" \
    --team-id "YOUR_TEAM_ID"
```

### Entitlements (macOS)

```xml
<!-- entitlements.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Allow file system access -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    
    <!-- Allow network access (if needed) -->
    <key>com.apple.security.network.client</key>
    <true/>
    
    <!-- Allow disk access -->
    <key>com.apple.security.device.disk</key>
    <true/>
    
    <!-- Disable sandbox for system access -->
    <key>com.apple.security.app-sandbox</key>
    <false/>
</dict>
</plist>
```

### Info.plist Configuration

```xml
<!-- macOS Info.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    
    <key>CFBundleExecutable</key>
    <string>USBSpeedTest</string>
    
    <key>CFBundleIdentifier</key>
    <string>com.usb-speedtest.app</string>
    
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    
    <key>CFBundleName</key>
    <string>USB Speed Test</string>
    
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    
    <key>CFBundleVersion</key>
    <string>1</string>
    
    <key>NSHighResolutionCapable</key>
    <true/>
    
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    
    <key>NSRequiresIPhoneOS</key>
    <false/>
</dict>
</plist>
```

---

## Linux Deployment

### Build Steps

```bash
#!/bin/bash
# build_linux.sh - Linux build script

set -e

echo "Building USB Speed Test for Linux..."

# Activate virtual environment
source venv/bin/activate

# Install AppImage dependencies
sudo apt-get install -y libfuse2 appimage-builder

# Build executable
pyinstaller pyinstaller.spec \
    --distpath=dist/linux \
    --buildpath=build \
    --specpath=build_specs

# Create AppImage
appimage-builder \
    --recipe AppImageBuilder.yml \
    --output "dist/USBSpeedTest-x86_64.AppImage"

# Make executable
chmod +x "dist/USBSpeedTest-x86_64.AppImage"

echo "Linux build complete!"
echo "Output: dist/USBSpeedTest-x86_64.AppImage"
```

### AppImageBuilder Configuration (AppImageBuilder.yml)

```yaml
version: 1

AppDir:
  path: ./AppDir
  app_info:
    id: com.usb-speedtest.app
    name: USB Speed Test
    icon: icon
    version: 1.0.0
    exec: usr/bin/USBSpeedTest
    exec_args: $@
  apt:
    arch: amd64
    sources:
      - sourceline: 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu/ jammy main'
    include:
      - python3.9-minimal
      - libpython3.9
      - python3-distutils
      - libfuse2
    exclude:
      - perl
      - perl-modules-5.34
  files:
    dist/linux/USBSpeedTest: /usr/bin/USBSpeedTest
    gui: /usr/share/usb-speedtest/gui
    src/modules: /usr/share/usb-speedtest/modules

  test:
    debian:
      image: ubuntu:22.04
      command: ./AppRun
      keep_going: true

AppImage:
  arch: x86_64
  image_format: squashfs
  sign: false
```

### Create Standalone Tarball

```bash
#!/bin/bash
# Create distributable tarball for Linux

mkdir -p dist/linux-portable
cp -r dist/linux/USBSpeedTest dist/linux-portable/
cp README.md dist/linux-portable/
cp LICENSE dist/linux-portable/

tar -czf dist/USBSpeedTest-1.0.0-linux-x86_64.tar.gz \
    -C dist linux-portable/

echo "Created portable tarball: dist/USBSpeedTest-1.0.0-linux-x86_64.tar.gz"
```

### DEB Package (Optional)

```bash
#!/bin/bash
# Create .deb package for Debian/Ubuntu

APP_NAME="usb-speedtest"
VERSION="1.0.0"
ARCH="amd64"

# Create package structure
mkdir -p deb_package/DEBIAN
mkdir -p deb_package/usr/bin
mkdir -p deb_package/usr/share/${APP_NAME}
mkdir -p deb_package/usr/share/applications

# Copy binary
cp dist/linux/USBSpeedTest deb_package/usr/bin/${APP_NAME}
chmod +x deb_package/usr/bin/${APP_NAME}

# Copy resources
cp -r gui deb_package/usr/share/${APP_NAME}/

# Create desktop entry
cat > deb_package/usr/share/applications/${APP_NAME}.desktop << EOF
[Desktop Entry]
Type=Application
Name=USB Speed Test
Icon=${APP_NAME}
Exec=${APP_NAME}
Categories=Utility;
Terminal=false
EOF

# Create control file
cat > deb_package/DEBIAN/control << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Architecture: ${ARCH}
Maintainer: Your Name <your@email.com>
Description: USB Device Speed Test and Monitoring Application
Homepage: https://your-website.com
Depends: libpython3.9, libfuse2
EOF

# Create deb file
dpkg-deb --build deb_package dist/${APP_NAME}_${VERSION}_${ARCH}.deb

echo "Created DEB package: dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
```

---

## Code Signing & Security

### Windows Code Signing

```batch
REM sign_windows.bat - Code signing script

REM Requires: 
REM  - signtool.exe (comes with Windows SDK)
REM  - Code signing certificate (.pfx)

set CERT_PATH="C:\path\to\certificate.pfx"
set CERT_PASSWORD="your-password"
set TIMESTAMP_URL="http://timestamp.comodoca.com/authenticode"
set EXE_PATH="dist\USBSpeedTest-1.0.0-installer.exe"

signtool sign /f %CERT_PATH% ^
    /p %CERT_PASSWORD% ^
    /t %TIMESTAMP_URL% ^
    /fd SHA256 ^
    /v %EXE_PATH%

echo Signing complete!
```

### macOS Code Signing

```bash
# sign_macos.sh

APP_PATH="dist/USBSpeedTest.app"
IDENTITY="Developer ID Application: Your Organization"

# Sign with entitlements
codesign --force --deep --verify \
    --sign "${IDENTITY}" \
    --options runtime \
    --entitlements entitlements.plist \
    "${APP_PATH}"

# Verify signature
codesign --verify --verbose=4 "${APP_PATH}"

# Check signature details
spctl -a -v -t exec "${APP_PATH}"
```

### GPG Signing for Linux/checksums

```bash
#!/bin/bash
# sign_releases.sh

# Generate SHA256 checksums
sha256sum dist/USBSpeedTest-*.{exe,dmg,AppImage,tar.gz} > CHECKSUMS.txt

# Sign checksums with GPG
gpg --armor --detach-sign CHECKSUMS.txt

# Verify signature
gpg --verify CHECKSUMS.txt.asc

echo "Release artifacts signed!"
```

---

## Distribution & Release

### Release Checklist

```
Pre-Release:
□ Update version number in config.py
□ Update CHANGELOG.md
□ Run full test suite
□ Build on all target platforms
□ Verify signatures
□ Create release notes

Release Steps:
□ Tag Git commit with version
□ Create GitHub Release
□ Upload binaries
□ Update website/documentation
□ Announce release (email, social media)

Post-Release:
□ Monitor for crash reports
□ Begin development on next version
□ Update roadmap
```

### GitHub Releases

```bash
#!/bin/bash
# Publish release to GitHub

VERSION="1.0.0"
RELEASE_NOTES="Release notes here..."

gh release create "v${VERSION}" \
    --title "USB Speed Test v${VERSION}" \
    --notes "${RELEASE_NOTES}" \
    --draft \
    --prerelease=false \
    dist/USBSpeedTest-${VERSION}-installer.exe \
    dist/USBSpeedTest-${VERSION}.dmg \
    dist/USBSpeedTest-${VERSION}-linux-x86_64.AppImage \
    dist/USBSpeedTest-${VERSION}-linux-x86_64.tar.gz \
    CHECKSUMS.txt \
    CHECKSUMS.txt.asc
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/build-release.yml

name: Build & Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.9'

jobs:
  build-windows:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller nsis
      
      - name: Build executable
        run: pyinstaller pyinstaller.spec
      
      - name: Create installer
        run: makensis installer.nsi
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: dist/USBSpeedTest-*-installer.exe

  build-macos:
    runs-on: macos-12
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller create-dmg
      
      - name: Build executable
        run: pyinstaller pyinstaller.spec
      
      - name: Create DMG
        run: bash scripts/build_macos.sh
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: macos-dmg
          path: dist/USBSpeedTest-*.dmg

  build-linux:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libfuse2 appimage-builder
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: bash scripts/build_linux.sh
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: linux-appimage
          path: dist/USBSpeedTest-*-linux-x86_64.AppImage

  create-release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-22.04
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - uses: actions/checkout@v3
      
      - name: Download all artifacts
        uses: actions/download-artifact@v3
        with:
          path: dist/
      
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/**/*
          body_path: RELEASE_NOTES.md
          draft: false
```

---

## Distribution Channels

### 1. Direct Download
- Host on organization website
- Provide checksums and signatures
- Mirror on multiple CDNs

### 2. Package Managers

#### Windows: Chocolatey
```xml
<!-- usb-speedtest.nuspec -->
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>usb-speedtest</id>
    <version>1.0.0</version>
    <title>USB Speed Test</title>
    <authors>Your Name</authors>
    <licenseUrl>https://opensource.org/licenses/MIT</licenseUrl>
    <projectUrl>https://your-website.com</projectUrl>
    <description>USB Device Speed Test and Monitoring Application</description>
  </metadata>
  <files>
    <file src="tools/**" target="tools" />
  </files>
</package>
```

#### macOS: Homebrew
```ruby
# Formula: usb-speedtest.rb

class UsbSpeedtest < Formula
  desc "USB Device Speed Test and Monitoring"
  homepage "https://your-website.com"
  url "https://releases.example.com/USBSpeedTest-1.0.0.dmg"
  sha256 "CHECKSUM_HERE"
  version "1.0.0"

  app "USBSpeedTest.app"
end
```

#### Linux: Snap
```yaml
# snapcraft.yaml

name: usb-speedtest
version: '1.0.0'
summary: USB Speed Test and Device Monitor
description: |
  Test and monitor USB device performance

grade: stable
confinement: strict

parts:
  usb-speedtest:
    plugin: python
    python-packages:
      - pywebview
      - psutil
      - pystray
      - plyer
      - Jinja2

apps:
  usb-speedtest:
    command: usr/bin/usb-speedtest
    plugs:
      - hardware-observe
      - system-observe
```

---

## Troubleshooting Build Issues

### Common Problems

#### 1. Missing Modules in PyInstaller

```python
# Add to pyinstaller.spec hiddenimports section
hiddenimports=[
    'pywebview.api',
    'pywebview.js.bridge',
    'PIL.Image',
    'psutil._psposix',  # or _psutil_windows
]
```

#### 2. Certificate/Signing Errors

```bash
# Windows: Verify signtool availability
where signtool.exe

# macOS: Check certificate
security find-identity -v -p codesigning

# Linux: Check GPG key
gpg --list-keys
```

#### 3. AppImage Issues

```bash
# Test AppImage
./USBSpeedTest-x86_64.AppImage --version

# Extract AppImage for debugging
./USBSpeedTest-x86_64.AppImage --appimage-extract
```

---

**End of Deployment & Packaging Guide**
