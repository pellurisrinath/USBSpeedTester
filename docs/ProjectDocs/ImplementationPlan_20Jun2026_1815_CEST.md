# Implementation Plan - Comparison Segregation & Dashboard Reports List

This document details the plan to isolate generated side-by-side performance comparisons into a dedicated comparisons folder `C:\ProgramData\USBSpeedTest\comparisions`, scan both directories on the backend, and present them dynamically in the GUI.

---

## Codebase Architecture & Key Improvements

1.  **Comparisons Folder Isolation**:
    *   Separate the reports folder (`C:\ProgramData\USBSpeedTest\reports`) and comparisons folder (`C:\ProgramData\USBSpeedTest\comparisions`).
    *   All single-device speed test HTML reports will reside under `reports/`.
    *   All side-by-side comparison HTML reports will reside under `comparisions/`.
2.  **Unified Reports Dashboard**:
    *   Update the backend API to scan both the `reports` and `comparisions` folders when retrieving the saved HTML reports list.
    *   Mark reports loaded from `comparisions/` with `report_type: "comparison"` and `reports/` with `report_type: "device"`.
    *   Merge and sort both sets of records by creation date so they display seamlessly in the same dashboard tab list.
3.  **Comparisons Directory Access**:
    *   Add an "Open Comparisons Folder" button in the GUI Reports tab, next to the "Open Reports Folder" button.
    *   Integrate the folder opening script on the backend.

---

## Proposed Changes

### Backend Modificiations

#### [MODIFY] [config.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/config.py)
*   Define `COMPARISONS_DIR = BASE_DIR / "comparisions"`.
*   Ensure that `ensure_directories()` creates the comparisons folder on startup.

#### [MODIFY] [speed_test.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/modules/speed_test.py)
*   Import `COMPARISONS_DIR`.
*   Change the destination folder of `generate_comparison_html_report()` from `REPORTS_DIR` to `COMPARISONS_DIR`.

#### [MODIFY] [main.py](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/src/main.py)
*   Import `COMPARISONS_DIR`.
*   Rewrite `get_reports_list(self, limit)` to:
    1. Scan `REPORTS_DIR` for `.html` files and add them with `report_type: "device"`.
    2. Scan `COMPARISONS_DIR` for `.html` files and add them with `report_type: "comparison"`.
    3. Merge, sort descending by creation timestamp, and slice by limit.

---

### Frontend UI Changes

#### [MODIFY] [index.html](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/index.html)
*   Modify the Reports Tab header to add `openComparisonsFolderBtn` next to `openReportsFolderBtn`.

#### [MODIFY] [app.js](file:///c:/Users/pellu/OneDrive/Documents/AntiGravity_USBSpeedTest/gui/app.js)
*   Register a click event handler for `openComparisonsFolderBtn` to read `data_directory` and open the local comparisons directory.

---

## Verification Plan

### Automated Compilation
*   Run `build.bat` and verify that the build compiles successfully without errors, generating the setup installer and standalone app.

### Manual Verification
1.  **Comparison Generation**: Select two session benchmarks and click "Compare". Verify the report is created inside `C:\ProgramData\USBSpeedTest\comparisions\compare_report_*.html`.
2.  **Dashboard Load**: Restart the app and go to the Reports tab. Verify that the previous comparisons are loaded and rendered with balance scale icons, alongside device benchmarks.
3.  **Comparisons Folder Button**: Click "Open Comparisons Folder" and check that it successfully opens the `C:\ProgramData\USBSpeedTest\comparisions` directory in Windows File Explorer.
