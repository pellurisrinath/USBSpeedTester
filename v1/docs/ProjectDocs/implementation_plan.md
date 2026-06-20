# USB Speed Test and Monitoring Application - Comparison Feature Implementation Plan

We will extend the application with a side-by-side benchmark comparison feature. This allows users to perform benchmarks on multiple USB drives and compile a comparative analysis report.

## Proposed Changes

### 1. Backend API (`main.py` & `speed_test.py`)
- **Session History Storage**: Track all speed tests conducted during the session.
- **Comparison Report Generator**: Implement a new function `generate_comparison_report(test_runs)` that creates a detailed, print-ready, plain-white comparison HTML report.
- The report will include:
  - Technical parameters for each device (Write/Read MB/s, Test size, File System, Bus Type).
  - Side-by-side structured comparison table.
  - Performance rankings (Fastest Read, Fastest Write, Overall Winner).
  - Clean, minimalist styling (plain white background, high contrast, tabular format) for easy reading/printing.

### 2. Frontend Changes (`gui/index.html`, `gui/style.css`, `gui/app.js`)
- Add a **Compare Panel** in the UI that displays when 2 or more tests are completed.
- Provide a button to "Generate Comparison Report".
- Render a side-by-side technical table directly on the screen.

---

## Verification Plan

### Manual Verification
1. Connect multiple USB storage devices (or test the same one multiple times).
2. Perform a speed test on Device A and then on Device B.
3. Verify that the comparison panel shows up in the UI with both results side-by-side.
4. Click "Generate Comparison Report" and verify the generated report is saved to `C:\ProgramData\UBSSpeedTest\compare_report_<timestamp>.html`.
5. Open the report and confirm it has a simple plain-white background and details the rankings.
