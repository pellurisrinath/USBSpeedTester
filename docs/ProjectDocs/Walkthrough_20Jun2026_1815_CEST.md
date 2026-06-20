# Walkthrough: Comparisons Directory Segregation & Dashboard Reports List

This document details the walkthrough of the improvements made to segregate side-by-side performance comparisons into a dedicated comparisons folder `C:\ProgramData\USBSpeedTest\comparisions`, scan both directories in the backend, and present them in the GUI.

---

## Changes Implemented

### 1. Comparisons Directory Segregation
*   **`src/config.py` [MODIFY]**:
    *   Defined `COMPARISONS_DIR = BASE_DIR / "comparisions"` (matching your requested path spelling `C:\ProgramData\USBSpeedTest\comparisions`).
    *   Updated `ensure_directories()` to automatically create the folder on application start.
*   **`src/modules/speed_test.py` [MODIFY]**:
    *   Imported `COMPARISONS_DIR` and updated the `generate_comparison_html_report()` function to write all comparison HTML reports directly into the new comparisons folder.

### 2. Unified Backend Scanning & History Loading
*   **`src/main.py` [MODIFY]**:
    *   Updated `get_reports_list(self, limit)` to scan both the device reports directory (`C:\ProgramData\USBSpeedTest\reports`) and the comparisons directory (`C:\ProgramData\USBSpeedTest\comparisions`).
    *   Automatically tags files in `reports/` as `device` type, and files in `comparisions/` as `comparison` type.
    *   Merges both lists and sorts them chronologically (descending) so they show up side-by-side in your dashboard's report feed.

### 3. Folder Navigation UI Controls
*   **`gui/index.html` [MODIFY]**: Added the **Open Comparisons Folder** button (`openComparisonsFolderBtn`) next to the "Open Reports Folder" button in the Reports Tab header.
*   **`gui/app.js` [MODIFY]**: Wired the click listener to query the data directory and launch the local comparisons folder `C:\ProgramData\USBSpeedTest\comparisions` directly in Windows File Explorer.

---

## Verification & Compilation Run
1.  **Build Execution**: Compiles successfully. Running `build.bat` outputs:
    *   `dist/USBSpeedTest.exe` (standalone executable)
    *   `dist/UBSSpeedtest_setup.exe` (all-in-one setup installer)
2.  **Security Scan**: A regex security analysis checked all source code for hardcoded secrets, password strings, or credentials.
    *   *Result*: Pass. No hardcoded keys are present.
