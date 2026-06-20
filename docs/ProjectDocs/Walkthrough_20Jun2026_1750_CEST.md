# Walkthrough: AI Timeout, Path Resolution, Logging, & Setup Installer

This document details the walkthrough of the bug fixes and features added to resolve the AI assistant timeouts, portable path resolution bug, log capture, and build a standalone setup wizard (`UBSSpeedtest_setup.exe`).

---

## Changes Implemented

### 1. AI Timeout & Logging Fixes
*   **`src/modules/ai_client.py` [MODIFY]**:
    *   Increased HTTP timeout from `30` to `120` seconds. Slow-running local LLMs (e.g., Gemma-4-12B or llama3 on local CPU/GPU) now have enough time to process system/chat history prompts and generate tokens without the connection failing with a timeout.
*   **`src/main.py` [MODIFY]**:
    *   Added standard stream redirection via a custom `Tee` class and `setup_logging()` function.
    *   All console output (stdout/stderr) from `pywebview`, helper scripts, and warnings are now mirrored to `app.log` in the persistent `logs/` directory.

### 2. Portable Path Resolution Fix
*   **`src/config.py` [MODIFY]**:
    *   Modified the base path detector to check if `sys.frozen` is active (running as compiled PyInstaller).
    *   If running frozen, it uses the directory containing the actual `.exe` file rather than the temporary `_MEIPASS` folder.
    *   *Effect*: Corrects the false-positive portable mode. The application now persistent-logs and persistent-saves configurations to `C:\ProgramData\USBSpeedTest` when installed there, and the "Open Reports Folder" button points to the correct location.

### 3. Standalone Installer Wizard
*   **`src/setup_installer.py` [NEW]**:
    *   Designed a lightweight Tkinter-based Windows setup installer compiled into a single executable `UBSSpeedtest_setup.exe`.
    *   Deploys `USBSpeedTest.exe` directly to `C:\ProgramData\USBSpeedTest`.
    *   Detects if an existing instance of `USBSpeedTest.exe` is currently running/locked and warns the user to close it.
    *   Dynamically creates Start Menu and Desktop shortcuts via native PowerShell COM objects.
    *   Includes a checkbox to auto-launch the application upon completion.
*   **`build.bat` [MODIFY]**:
    *   Updated the script to first compile the main `dist/USBSpeedTest.exe` and then compile `dist/UBSSpeedtest_setup.exe` bundling the compiled app binary.

---

## Verification & Compilation Run
1.  **Build Execution**: Compiles successfully. Running `build.bat` outputs:
    *   `dist/USBSpeedTest.exe` (standalone executable)
    *   `dist/UBSSpeedtest_setup.exe` (all-in-one setup installer)
2.  **Security Scan**: A regex security analysis checked all source code for hardcoded secrets, password strings, or credentials.
    *   *Result*: Pass. No hardcoded keys are present.
