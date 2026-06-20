# Walkthrough: Configuration Persistence, Settings Export, & Installer Fixes

This document details the walkthrough of the improvements made to persist configurations in `C:\ProgramData\USBSpeedTest`, implement a settings export feature, and compile the final executables.

---

## Changes Implemented

### 1. Enforced Configuration Persistence
*   **`src/config.py` [MODIFY]**:
    *   Bypassed portable mode check on Windows, enforcing `BASE_DIR = Path("C:\ProgramData\USBSpeedTest")`.
    *   *Effect*: All configurations, logs, and HTML benchmark reports are written to this central folder on Windows regardless of the executable running location. Deleting the executable, running portable copies, or updating/reinstalling the application will check for and reuse the existing configuration file, preserving user configurations.

### 2. Settings Export Feature
*   **`gui/index.html` [MODIFY]**: Added the **Export Configuration** button to the Settings Modal.
*   **`gui/app.js` [MODIFY]**: Wired the click listener to request settings export from the backend.
*   **`src/main.py` [MODIFY]**:
    *   Implemented `export_configuration` in `BackendAPI`.
    *   Generates default name template: `USBSpeedTest_<MachineName>_<ddMMMyyyy>_<HHmm>_<timezone>.cfg` (e.g. `USBSpeedTest_w01bf41ey_20June2026_1807_cest.cfg`).
    *   Opens a native file save dialog via `pywebview` for the user to choose their export destination and saves the configuration as structured JSON.

### 3. Setup Installer Wizard Improvements
*   **`src/setup_installer.py` [MODIFY]**:
    *   **Process Launch Fix**: Removed the mutually exclusive `subprocess.CREATE_NEW_CONSOLE` flag. Auto-launching the application now runs successfully without crashing the installer with `[WinError 87] The parameter is incorrect`.
    *   **Buttons Visibility Fix**: Relocated `btn_frame` to `side=tk.BOTTOM` to avoid grid clipping, increased window size to `540x400` for layout padding, and styled the buttons with Purple 500 and Slate 700 backgrounds with white text for high contrast.
    *   **Verbose Logging**: Implemented a comprehensive logging module inside the installer script. It automatically writes detailed execution logs—such as system parameters, lock checks, PowerShell shortcut commands and outputs, and traceback diagnostics—to a persistent log file at **`C:\ProgramData\USBSpeedTest\setup_install.log`**.
*   **`build.bat` [MODIFY]**:
    *   Refined compilation scripts to compile the standalone `dist/USBSpeedTest.exe` and package it inside `dist/UBSSpeedtest_setup.exe`.

---

## Verification & Compilation Run
1.  **Build Execution**: Compiles successfully. Running `build.bat` outputs:
    *   `dist/USBSpeedTest.exe` (standalone executable)
    *   `dist/UBSSpeedtest_setup.exe` (all-in-one setup installer)
2.  **Security Scan**: A regex security analysis checked all source code for hardcoded secrets, password strings, or credentials.
    *   *Result*: Pass. No hardcoded keys are present.
