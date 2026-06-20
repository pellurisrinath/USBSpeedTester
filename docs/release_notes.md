# GitLab Technical Release Notes - USB Speed Test & Monitor v1.1.0

## Release Summary
We are proud to release **v1.1.0** of the **USB Speed Test & Monitor Utility**, introducing high-fidelity, side-by-side USB storage comparison functionality, detailed leaderboards, and print-ready minimalist HTML report creation for multi-drive testing sessions.

---

## What's New in v1.1.0

1. **Side-by-Side Comparison UI**
   - Automatically tracks consecutive speed test runs during the application session.
   - Shows an interactive side-by-side technical specification table in the UI whenever 2 or more tests are completed.
   - Compares read speed, write speed, combined throughput, and mount points in real time.

2. **Technical Comparison HTML Report**
   - Introduces a "Generate Comparison HTML Report" feature.
   - Saves clean, print-ready, plain-white background reports (meeting executive readability and high-contrast styling specifications) detailing:
     - USB Device Model Performance Leaderboard (Fastest Read, Fastest Write, Overall Champion).
     - Full side-by-side technical parameters (throughput speeds, durations, file systems, mount points, serial numbers).
   - Saved locally at `C:\ProgramData\USBSpeedTest\compare_report_<timestamp>.html` (or `~/.USBSpeedTest/` on macOS/Linux).

---

## Key Features Retained from v1.0.0

- **Platform Independence**: Identical performance on Windows, macOS, and Linux.
- **Background Health Monitor**: Automated background loop monitoring space; notifies user instantly if any USB drive falls below 10% space threshold.
- **Premium Glassmorphic UI**: Dashboard interface containing radial progress speedometers, HSL gradients, and live test staging logs.
- **Standalone Binary Packaging**: Easy packaging into a single file with PyInstaller.

---

## Compilation & Packaging

To compile this updated version into a standalone binary:
```bash
pyinstaller --noconsole --onefile --name USBSpeedTest --add-data "gui;gui" src/main.py
```
Copy the resulting binary `USBSpeedTest.exe` from the `dist` directory into:
`C:\ProgramData\USBSpeedTest\USBSpeedTest.exe`
