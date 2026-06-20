# Walkthrough: AI Timeout, Path Resolution, Logging, & Setup Installer

This document details the walkthrough of the bug fixes and features added to resolve the AI assistant timeouts, portable path resolution bug, log capture, and build a standalone setup wizard (`UBSSpeedtest_setup.exe`).

---

## Changes Implemented

### 1. AI Timeout & Logging Fixes
*   **`src/modules/ai_client.py` [MODIFY]**:
    *   Increased HTTP timeout from `30` to `300` seconds (5 minutes). Slow-running local LLMs (e.g., Gemma-4-12B or llama3 on local CPU/GPU) now have plenty of time to process system/chat history prompts and generate reasoning/response tokens without the connection failing with a timeout.
*   **`src/main.py` [MODIFY]**:
    *   Added standard stream redirection via a custom `Tee` class and `setup_logging()` function.
    *   All console output (stdout/stderr) from `pywebview`, helper scripts, and warnings are now mirrored to `app.log` in the persistent `logs/` directory.

### 2. Configuration Path Resolution & Persistence
*   **`src/config.py` [MODIFY]**:
    *   Updated path resolution so that on Windows (`sys.platform == 'win32'`), `BASE_DIR` is **always** set to `C:\ProgramData\USBSpeedTest`, bypassing the portable mode check.
    *   *Effect*: The configuration (`config.json`), logs (`app.log`), and reports are saved to a central, persistent location. When you remove, re-run, or reinstall the application, the app automatically checks for and reuses the existing configuration file, preserving all your settings.
*   **`gui/index.html` [MODIFY]**:
    *   Added an **Export Configuration** button (`exportConfigBtn`) to the Settings modal.
*   **`gui/app.js` [MODIFY]**:
    *   Wired the button to invoke the backend's export configuration method, showing visual toast notifications upon completion.
*   **`src/main.py` [MODIFY]**:
    *   Implemented `export_configuration()` to generate a default filename using the machine name (lowercase), timestamp, and timezone: `USBSpeedTest_<MachineName>_<ddMMMyyyy>_<HHmm>_<timezone>.cfg`.
    *   Opens a native file save dialog via `pywebview` for the user to choose their export destination and saves the configuration as structured JSON.

### 3. Standalone Installer Wizard
*   **`src/setup_installer.py` [NEW]**:
    *   Designed a lightweight Tkinter-based Windows setup installer compiled into a single executable `UBSSpeedtest_setup.exe`.
    *   Deploys `USBSpeedTest.exe` directly to `C:\ProgramData\USBSpeedTest`.
    *   Detects if an existing instance of `USBSpeedTest.exe` is currently running/locked and warns the user to close it.
    *   Dynamically creates Start Menu and Desktop shortcuts via native PowerShell COM objects.
    *   Includes a checkbox to auto-launch the application upon completion.
    *   **Layout and Visibility Fixes**: Increased geometry to `540x400` and packed `btn_frame` with `side=tk.BOTTOM` to prevent button clipping. Styled the buttons with Slate 700 and Purple 500 backgrounds with white text for high contrast and clear visibility in dark mode.
    *   **Process Launch Fix**: Removed the mutually exclusive `subprocess.CREATE_NEW_CONSOLE` creation flag from the detached Popen call. This resolves `[WinError 87] The parameter is incorrect` that crashed the installer during auto-launch.
    *   **Verbose Logging**: Implemented a comprehensive logging module inside the installer script. During execution, it automatically writes detailed execution details—such as system parameters, source/destination sizes, lock checks, PowerShell shortcut commands and outputs, and complete traceback diagnostics for any errors—to a persistent log file at **`C:\ProgramData\USBSpeedTest\setup_install.log`**.
*   **`build.bat` [MODIFY]**:
    *   Updated the script to first compile the main `dist/USBSpeedTest.exe` and then compile `dist/UBSSpeedtest_setup.exe` bundling the compiled app binary.

---

## Verification & Compilation Run
1.  **Build Execution**: Compiles successfully. Running `build.bat` outputs:
    *   `dist/USBSpeedTest.exe` (standalone executable)
    *   `dist/UBSSpeedtest_setup.exe` (all-in-one setup installer)
2.  **Security Scan**: A regex security analysis checked all source code for hardcoded secrets, password strings, or credentials.
    *   *Result*: Pass. No hardcoded keys are present.
