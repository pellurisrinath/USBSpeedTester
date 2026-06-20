# Implementation Plan - Bug Fixes & Standalone Installer

This document outlines the implementation plan to address the AI timeout errors, correct the portable directory resolution path bug, enable local file-based logging, and deliver a standalone setup installer (`UBSSpeedtest_setup.exe`) for the USB Speed Test & Monitor application.

---

## User Review Required

> [!NOTE]
> The setup installer `UBSSpeedtest_setup.exe` is created dynamically under the `dist/` directory during compilation. It bundles `USBSpeedTest.exe` inside it, meaning the user only needs to share/deploy the single setup executable. It installs the application to `C:\ProgramData\USBSpeedTest` and creates start menu and desktop shortcuts.

> [!IMPORTANT]
> Because PyInstaller compiles all dependencies (including Python and Qt/WebView wrappers) into a standalone executable, there is **no need** for the target machine to have Python or other pre-requisites installed. The setup wizard explains this to the user during installation.

---

## Proposed Changes

### 1. Backend Modifications

#### [MODIFY] [ai_client.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/modules/ai_client.py)
*   **Timeout Extension**: Increase the standard `urllib.request.urlopen` timeout parameter from `30` seconds to `120` seconds. This accommodates slow-running local LLM models (e.g. llama3/gemma running on consumer CPUs/GPUs) which may take up to a minute to process prompt contexts and start generating response tokens.

#### [MODIFY] [config.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/config.py)
*   **Frozen Path Detection (PyInstaller)**: Update `APP_DIR` resolution to check if the script is running in a frozen PyInstaller state (`sys.frozen`).
    *   If frozen: `APP_DIR` is set to `Path(sys.executable).parent` (the folder containing `USBSpeedTest.exe`).
    *   If not frozen (dev mode): `APP_DIR` is set to `Path(__file__).parent.parent` (the workspace root directory).
    *   *Rationale*: Previously, when running as a frozen executable, `APP_DIR` resolved to the temporary extraction directory `sys._MEIPASS`, which is always writable. This falsely activated portable mode, writing logs/configs to temporary folders that were deleted on exit. Correcting this ensures the app correctly identifies write permissions in its installation folder (like `C:\ProgramData\USBSpeedTest`), deploying logs and configs to persistent locations.

#### [MODIFY] [main.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/main.py)
*   **Stdout/Stderr File Logging**: Define a robust `Tee` streaming class and `setup_logging` function.
    *   Redirects all standard output (`sys.stdout`) and standard error (`sys.stderr`) into `C:\ProgramData\USBSpeedTest\logs\app.log` (or `<portable_dir>\logs\app.log` if in portable mode).
    *   Ensures console outputs (including pywebview warnings and traceback logs) are written to disk for user inspection, resolving the "no logs created" issue.
    *   Initializes logging as the first step of `main()`.

### 2. Standalone Installer & Compilation

#### [NEW] [setup_installer.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/setup_installer.py)
*   **Wizard Interface**: Implement a lightweight, dark-themed Tkinter wizard (`SetupInstaller`) matching the primary design colors (slate and purple/violet).
*   **Copy & Overwrite Protection**: Creates the destination folder `C:\ProgramData\USBSpeedTest`, and securely copies the bundled executable. Checks if the destination executable is locked/running, and prompts the user to close it.
*   **PowerShell Shortcut Generator**: Generates Desktop and Start Menu programs shortcuts without requiring third-party library dependencies (like `pywin32`) by invoking lightweight PowerShell COMObject commands.
*   **Auto-Launch Helper**: Detaches the newly installed `USBSpeedTest.exe` process to run standalone and exits setup.

#### [MODIFY] [build.bat](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/build.bat)
*   **Consecutive Compilations**:
    1. Compiles `USBSpeedTest.spec` using PyInstaller to generate `dist/USBSpeedTest.exe`.
    2. Runs PyInstaller on `src/setup_installer.py` in `--onefile` and `--noconsole` mode, passing `--add-data "dist/USBSpeedTest.exe;."` to embed the compiled application directly inside `dist/UBSSpeedtest_setup.exe`.

---

## Verification Plan

### Automated Compilation
*   Run `build.bat` and verify that the build concludes successfully without errors, generating:
    *   `dist/USBSpeedTest.exe`
    *   `dist/UBSSpeedtest_setup.exe`

### Manual Verification
1.  **AI Request Timeout**: Configure settings to connect to the local LM Studio model and ask it to analyze speed test results. Confirm that response generation completes successfully even if it takes more than 30 seconds.
2.  **Installer Test**:
    *   Run `dist/UBSSpeedtest_setup.exe`.
    *   Verify the GUI looks modern and dark-themed.
    *   Confirm installation deploys files to `C:\ProgramData\USBSpeedTest`.
    *   Confirm Desktop and Start Menu shortcuts are created and point to `C:\ProgramData\USBSpeedTest\USBSpeedTest.exe`.
    *   Ensure the app auto-launches upon completion.
3.  **Logs and Reports Location**:
    *   Verify that `app.log` is created and populated under `C:\ProgramData\USBSpeedTest\logs\`.
    *   Verify that speed test reports are saved to `C:\ProgramData\USBSpeedTest\reports\`.
    *   Verify that the "Open Reports Folder" button in the dashboard successfully opens `C:\ProgramData\USBSpeedTest\reports`.
