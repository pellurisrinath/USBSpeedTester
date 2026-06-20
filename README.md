# USB Speed Utility & Monitor 🚀

A premium, lightweight, cross-platform desktop application built with Python (`pywebview`) and a responsive web frontend. The tool allows users to diagnose connected USB peripherals, run accurate read/write speed benchmarks, perform side-by-side performance comparisons, and monitor disk space with system tray integrations.

---

## 📸 Key Features

*   **USB Peripheral Analyzer**: Automatically lists all connected USB hardware (Storage Drives, Audio Devices, Cameras, Input Devices, and other peripherals) using native system commands (PowerShell/WMI, `diskutil`, `lsusb`).
*   **Speed Benchmarking**: Executes precise write and read tests with real-time speedometers. Enforces hardware cache flushes (`os.fsync`) to prevent RAM buffering from inflating benchmark results.
*   **Side-by-Side Comparison**: Select multiple previous test runs to compile performance matrices.
*   **Disk Space Analysis**: High-contrast visual storage bars displaying occupied vs. free capacity.
*   **Background Monitoring & Tray Integration**: Runs as a lightweight system tray service. Automatically runs checkups to alert users of low disk space on connected USB storage devices via native system toasts.
*   **Local-Only Configuration**: Saves settings locally inside your run directory or user data folder. No telemetry, no external connections.

---

## 🛠️ Architecture

```mermaid
graph TD
    UI["HTML / CSS / JS Dashboard (gui/)"] <--> |PyWebView Bridge| PyAPI["main.py Backend API (src/)"]
    PyAPI --> USB["usb_detector.py (WMI / lsusb)"]
    PyAPI --> Bench["speed_test.py (Write/Read Benchmark)"]
    PyAPI --> Service["monitor_service.py (Tray & Alert Loop)"]
    Bench --> |Saves HTML Report| Reports["C:/ProgramData/UBSSpeedTest/reports/"]
    Service --> |Toast Notifications| User["Desktop Toasts"]
```

---

## 📁 Repository Structure (GitHub Standards)

This repository maintains a clean, modular structure conforming to standard Python packaging and GitHub best practices:

```text
├── docs/                       # Project documentation
│   └── ProjectDocs/            # BRD, PRD, and Implementation plans
├── gui/                        # Frontend UI assets
│   ├── app.js                  # Frontend controllers and API bridge
│   ├── index.html              # Dashboard interface structure
│   └── style.css               # Premium dark glassmorphic design system
├── src/                        # Main application source code
│   ├── main.py                 # Application entry point & webview window loop
│   ├── config.py               # Configuration loading/saving logic
│   └── modules/                # Core modular services
│       ├── monitor_service.py  # Background space checker & tray icon
│       ├── platform_utils.py   # Cross-platform file/folder opener utilities
│       ├── speed_test.py       # Speed test block writing/reading algorithms
│       └── usb_detector.py     # USB peripheral & storage enumerators
├── build.bat                   # Compilation script for PyInstaller
├── USBSpeedTest.spec           # PyInstaller build specification
├── .gitignore                  # Git exclusion rules
└── README.md                   # Project overview & documentation
```

---

## ⚙️ Getting Started

### Prerequisites

Ensure you have Python 3.10+ installed. Install the required libraries:

```bash
pip install pywebview psutil pystray plyer Pillow
```

### Running the Application

To run the application from source code:

```bash
python src/main.py
```

### Compiling Standalone Executable

You can compile the utility into a single standalone executable (which embeds python and all assets) using `PyInstaller`. 

Run the build script:

```cmd
build.bat
```
The compiled output will be generated under `dist/USBSpeedTest.exe`.

---

## 🔒 Security & Privacy Statement

This application is designed with privacy-first principles:
1. **No External Telemetry**: The app operates fully locally and does not upload metrics to any cloud servers.
2. **Local Storage**: All settings are stored in `config.json` inside the user’s local folders (`C:\ProgramData\UBSSpeedTest` or the installation directory).
3. **No Hardcoded Keys**: The application contains no embedded API keys, secret credentials, or personal tokens. If you utilize cloud integrations, keys are stored locally on your machine and are only transmitted directly to the official vendor APIs (e.g. OpenAI, Anthropic) without intermediate proxies.

---

## 📄 License

This project is licensed under the MIT License. Feel free to modify, distribute, and integrate it into your own systems.
