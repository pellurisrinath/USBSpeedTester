# USB Speed Utility & Monitor 🚀

A premium, lightweight, cross-platform desktop application built with Python (`pywebview`) and a responsive web frontend. The tool allows users to diagnose connected USB peripherals, run accurate read/write speed benchmarks, perform side-by-side performance comparisons, and monitor disk space with system tray integrations.

---

## 🖥️ User Interface Tour

| | |
|---|---|
| 📸 **[View Full UI Tour with Screenshots →](docs/UserInterfaceTour.md)** | Devices · Storage · Speed Test · Comparison · Reports · AI Assistant · Settings |

> All 14 screenshots across 8 feature sections — click above to explore the full visual walkthrough.

---

## ✨ Key Features

*   **USB Peripheral Analyzer**: Automatically lists all connected USB hardware (Storage Drives, Audio Devices, Cameras, Input Devices, and other peripherals) along with driver details (provider, version, date) using Windows PnP APIs, `diskutil` (macOS), or `lsusb` (Linux).
*   **Speed Benchmarking**: Executes precise write and read tests with real-time speedometers. Enforces hardware cache flushes (`os.fsync`) to prevent RAM buffering from inflating benchmark results.
*   **AI Chatbot Assistant**: A context-aware chatbot supporting Ollama, Claude, OpenAI, Gemini, and Custom OpenAI-compatible endpoints to analyze speed tests, explain file systems, and troubleshoot slowness.
*   **Web Specs lookup & Driver Context**: Dynamically looks up hardware specifications on DuckDuckGo Lite when asked about device performance. Integrates device driver details in the system context. Reports back with offline diagnostics if the host is disconnected.
*   **Dynamic Guardrails File**: Chatbot guidelines are loaded at query time from `C:\ProgramData\USBSpeedTest\Guardrails.md`. Administrators can adjust rules dynamically without recompiling.
*   **UI Clipboard Integrations**: Copy buttons (`📋 Copy`) inside the chat interface let users copy slowness reports or templates to the clipboard in one click.
*   **Side-by-Side Comparison**: Select multiple previous test runs to compile performance matrices saved under `C:\ProgramData\USBSpeedTest\comparisions`.
*   **Disk Space Analysis**: High-contrast visual storage bars displaying occupied vs. free capacity.
*   **Background Monitoring & Tray Integration**: Runs as a lightweight system tray service. Automatically runs checkups to alert users of low disk space on connected USB storage devices via native system toasts.
*   **Local-Only Configuration**: Saves settings locally inside your run directory or user data folder. No telemetry, no external connections.

---

## 🛠️ Architecture

```mermaid
graph TD
    UI["HTML / CSS / JS Dashboard (gui/)"] <--> |PyWebView Bridge| PyAPI["main.py Backend API (src/)"]
    PyAPI --> USB["usb_detector.py (WMI / PnP Drivers)"]
    PyAPI --> Bench["speed_test.py (Write/Read Benchmark)"]
    PyAPI --> Service["monitor_service.py (Tray & Alert Loop)"]
    PyAPI --> Search["online_search.py (DuckDuckGo Specs Crawl)"]
    PyAPI --> Guard["C:/ProgramData/USBSpeedTest/Guardrails.md"]
    Bench --> |Saves HTML Report| Reports["C:/ProgramData/USBSpeedTest/reports/"]
    Service --> |Toast Notifications| User["Desktop Toasts"]
```

---

## 📁 Repository Structure (GitHub Standards)

This repository maintains a clean, modular structure conforming to standard Python packaging and GitHub best practices:

```text
├── docs/                       # Project documentation
│   ├── images/                 # User interface screenshots (14 images)
│   ├── ProjectDocs/            # BRD, PRD, Implementation plans & walkthroughs
│   ├── SCREENSHOTS.md          # Quick screenshots index
│   ├── UserInterfaceTour.md    # Full visual UI tour with all screenshots embedded
│   └── User_Guide.md           # Friendly documentation for non-technical users
├── gui/                        # Frontend UI assets
│   ├── app.js                  # Frontend controllers and API bridge
│   ├── index.html              # Dashboard interface structure
│   └── style.css               # Premium dark glassmorphic design system
├── src/                        # Main application source code
│   ├── main.py                 # Application entry point & webview window loop
│   ├── config.py               # Configuration loading/saving/guardrail creation
│   └── modules/                # Core modular services
│       ├── monitor_service.py  # Background space checker & tray icon
│       ├── online_search.py    # Lightweight DDG specs crawler
│       ├── platform_utils.py   # Cross-platform file/folder opener utilities
│       ├── speed_test.py       # Speed test block writing/reading algorithms
│       └── usb_detector.py     # USB peripheral, storage & driver enumerators
├── build.bat                   # Compilation script launcher for Windows
├── build.py                    # Cross-platform PyInstaller compiler & packager
├── build.sh                    # Compilation script launcher for macOS / Linux
├── USBSpeedTest.spec           # PyInstaller build specification
├── requirements.txt            # Python dependencies manifest
├── .gitignore                  # Git exclusion rules
├── CHANGELOG.md                # Full version history and release notes
├── README.md                   # Project overview & documentation
```

---

## ⚙️ Getting Started & Installation

Follow these instructions to download the project locally, set up the environment, run the application, and compile it into standalone installers.

### 1. Download the Project Locally

Clone the repository to your local machine:

```bash
git clone https://github.com/pellurisrinath/USBSpeedTester.git
cd USBSpeedTester
```

### 2. Environment Setup (Recommended)

It is highly recommended to use a Python virtual environment to keep dependencies isolated:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (Command Prompt):
call venv\Scripts\activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required python libraries using the provided `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Running the Application from Source

Launch the desktop interface by running the main entry script:

```bash
python src/main.py
```

### 5. Compiling Standalone Installers & Executables

You can compile the application into deployment-ready executables and installers for **Windows**, **Linux**, and **macOS**. The Python build controller (`build.py`) detects the host operating system and compiles the corresponding installer under the `dist/` directory.

```bash
# On Windows (compiles USBSpeedTest.exe and UBSSpeedtest_setup.exe wizard):
build.bat

# On Linux (compiles standalone binary and packages it into a Debian .deb package):
./build.sh

# On macOS (compiles .app bundle and packages it into a .dmg disk image):
./build.sh
```

Once complete, your deployment-ready files will be located in:
📁 **`dist/`**

---

## 🔒 Security & Privacy Statement

This application is designed with privacy-first principles:
1. **No External Telemetry**: The app operates fully locally and does not upload metrics to any cloud servers.
2. **Local Storage**: All settings and guardrails are stored in `config.json` and `Guardrails.md` inside `C:\ProgramData\USBSpeedTest` or the local user folders.
3. **No Hardcoded Keys**: The application contains no embedded API keys, secret credentials, or personal tokens. If you utilize cloud integrations, keys are stored locally on your machine and are only transmitted directly to the official vendor APIs (e.g. OpenAI, Anthropic) without intermediate proxies.

---

## 📄 License

This project is licensed under the MIT License. Feel free to modify, distribute, and integrate it into your own systems.

---

## Support

If you like the project and want to support it, you can buy me a coffee. It will help me to keep working on the project.

<a href='https://ko-fi.com/pellurisrinath' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

or you can sponsor me on GitHub.

A huge thank you to everyone who has supported Page Assist through [Ko-fi](https://ko-fi.com/pellurisrinath) and [GitHub Sponsors](https://github.com/sponsors/pellurisrinath) — your generosity keeps this project going. 💛

