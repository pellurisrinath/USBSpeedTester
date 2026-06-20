import os
import sys
import shutil
import subprocess

def run_cmd(cmd, shell=False):
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    subprocess.run(cmd, shell=shell, check=True)

def build_windows():
    print("=== Building for Windows ===")
    # 1. Compile main application
    run_cmd(["pyinstaller", "USBSpeedTest.spec"])
    # 2. Compile setup installer
    run_cmd(["pyinstaller", "UBSSpeedtest_setup.spec"])
    print("\nDone! Windows standalone executable and setup installer are under the 'dist' directory.")

def build_linux():
    print("=== Building for Linux ===")
    # 1. Compile main application
    run_cmd(["pyinstaller", "USBSpeedTest.spec"])
    
    # 2. Package as a .deb file (apt compatible)
    print("Packaging as Debian (.deb) package...")
    deb_dir = "/tmp/usb-speedtest-deb"
    if os.path.exists(deb_dir):
        shutil.rmtree(deb_dir)
        
    os.makedirs(f"{deb_dir}/DEBIAN", exist_ok=True)
    os.makedirs(f"{deb_dir}/usr/bin", exist_ok=True)
    os.makedirs(f"{deb_dir}/usr/share/applications", exist_ok=True)
    
    # Copy binary
    shutil.copy("dist/USBSpeedTest", f"{deb_dir}/usr/bin/usb-speedtest")
    
    # Write control file
    control_content = """Package: usb-speedtest
Version: 1.1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: USB Speed Test Team <support@usbspeedtest.com>
Description: USB Speed Test and Monitor Utility
"""
    with open(f"{deb_dir}/DEBIAN/control", "w", encoding="utf-8") as f:
        f.write(control_content)
        
    # Write desktop entry
    desktop_content = """[Desktop Entry]
Name=USB Speed Test
Comment=USB Speed Test and Monitor Utility
Exec=/usr/bin/usb-speedtest
Icon=usb-speedtest
Type=Application
Terminal=false
Categories=Utility;
"""
    with open(f"{deb_dir}/usr/share/applications/usb-speedtest.desktop", "w", encoding="utf-8") as f:
        f.write(desktop_content)
        
    # Run dpkg-deb to package it
    run_cmd(["dpkg-deb", "--build", deb_dir, "dist/usb-speedtest_1.1.0_amd64.deb"])
    shutil.rmtree(deb_dir)
    print("\nDone! Linux .deb package is available under 'dist/usb-speedtest_1.1.0_amd64.deb'.")

def build_macos():
    print("=== Building for macOS ===")
    # 1. Compile main application (outputs .app bundle on macOS)
    run_cmd(["pyinstaller", "USBSpeedTest.spec"])
    
    # 2. Package as a .dmg file
    print("Packaging as Disk Image (.dmg)...")
    dmg_path = "dist/USBSpeedTest.dmg"
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
        
    # Run hdiutil to create dmg from the compiled app bundle
    run_cmd([
        "hdiutil", "create", "-volname", "USB Speed Test",
        "-srcfolder", "dist/USBSpeedTest.app", "-ov", "-format", "UDZO", dmg_path
    ])
    print("\nDone! macOS .dmg package is available under 'dist/USBSpeedTest.dmg'.")

def main():
    # Make sure we install requirements first
    print("Installing requirements...")
    run_cmd([sys.executable, "-m", "pip", "install", "pywebview", "psutil", "pystray", "plyer", "Pillow", "pyinstaller"])
    
    if sys.platform == "win32":
        build_windows()
    elif sys.platform.startswith("linux"):
        build_linux()
    elif sys.platform == "darwin":
        build_macos()
    else:
        print(f"Unsupported OS: {sys.platform}")
        sys.exit(1)

if __name__ == "__main__":
    main()
