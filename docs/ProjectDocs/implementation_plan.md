# USB Speed Test and Monitoring Application - Full Technical Specification Alignment Plan

We will align the project's folder structure, backend APIs, and frontend interface with the comprehensive design detailed in the specification documents in `docs/ProjectDocs/files/`.

## Restructuring Plan

We will reorganize the codebase to follow the layout specified in `USB_SpeedTest_Technical_Spec.md`:

```
USBSpeedTest/
├── src/
│   ├── main.py                    # App entry point
│   ├── config.py                  # Configurations & constants
│   │
│   └── modules/
│       ├── __init__.py
│       ├── usb_detector.py        # USB device enumeration
│       ├── speed_test.py          # Benchmark logic
│       ├── report_generator.py    # HTML report creation & comparisons
│       ├── monitor_service.py     # Background monitoring, notifications & tray
│       └── platform_utils.py      # Platform specifics & fallbacks
│
└── gui/
    ├── index.html                 # Main UI structure with Tab Navigation
    ├── style.css                  # Styles (glassmorphism theme)
    └── app.js                     # Main JS controller & API bridge
```

---

## Detailed Component Alignments

### 1. Unified Configuration & Platform Abstractions (`config.py` & `platform_utils.py`)
- **JSON Configuration**: Support `config.json` loading and updating via the API, storing settings like checking interval (default: 60s), low disk space warning threshold (default: 10%), default test size (default: 100MB).
- **Directory Verification**: Programmatic creation of directories:
  - Windows: `C:\ProgramData\UBSSpeedTest` (with subdirectories `reports` and `logs`)
  - macOS: `~/Library/Application Support/USBSpeedTest`
  - Linux: `~/.local/share/usb-speedtest`

### 2. Comprehensive Backend API Bridge
Expose the full set of bridge endpoints detailed in `API_Frontend_Implementation.md`:
- `get_all_devices()`, `get_storage_devices()`, `get_peripheral_devices()`, `get_devices_by_type(device_type)`, `get_device_details(device_id)`
- `get_space_info(device_id)`
- `run_speed_test(device_id, test_size_mb)`
- `get_test_history()`, `cancel_speed_test()`
- `generate_device_report(test_id)`
- `generate_comparison_report(test_ids)`
- `get_reports_list(limit)`
- `open_report(report_path)`
- `get_app_info()`, `get_system_info()`
- `get_config()`, `update_config(config_dict)`
- `open_path(path)`

### 3. Frontend Tabbed Dashboard Interface
Implement the Tab Navigation in the GUI as shown in the frontend specs:
1. **Devices Tab**: Grid showing connected USB devices, filtered by type (Storage, Audio, Input, etc.).
2. **Storage Tab**: Disk space analysis with visual HSL percentage bars.
3. **Speed Test Tab**: Test size options, circular gauge speed meters, and benchmarking progress logs.
4. **Comparison Tab**: Side-by-side benchmark comparison matrix.
5. **Reports Tab**: List of generated reports with clickable buttons to view them.
- Modals for Settings and test cancel options.

---

## Verification Plan

### Manual Verification
1. Run `python src/main.py`.
2. Confirm the window loads the new tabbed layout (Devices, Storage, Speed Test, Comparison, Reports).
3. Test WMI/Powershell querying via `get_all_devices()`.
4. Run consecutive speed tests on multiple drives, check that they populate the Comparison tab, and compile a side-by-side Technical Comparison Report.
5. Verify the background low space alerts trigger OS notifications.
6. Verify PyInstaller compiles the restructured repository into the standalone binary `USBSpeedTest.exe`.
