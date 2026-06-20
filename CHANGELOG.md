# Changelog

All notable changes to **USB Speed Test & Monitor** are documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

---

## [1.3.0] — 2026-06-20

### Fixed
- **Critical: USB devices not showing in Devices tab** — The previous release introduced `Win32_PnPSignedDriver` lookups inside a per-device PowerShell loop (`get_usb_storage_devices` and `get_usb_peripherals`). On machines with many USB peripherals this caused the PowerShell script to run for 60–90+ seconds, silently failing and returning an empty device list. Fix: pre-fetch all driver entries once into a PowerShell hashtable (`$allDrivers = @{}`) and perform O(1) in-memory lookups per device. Added explicit `timeout=30` to all `subprocess.run()` calls.
- Added `-ErrorAction SilentlyContinue` to `Get-PnpDevice` and `Get-CimInstance` calls to prevent partial failures from crashing the entire script.

### Changed
- Removed the **"Filter by Type"** dropdown from the Devices tab — the application is scoped to USB devices only, making the filter redundant.
- `create_shortcut()` in the setup installer now sets `IconLocation` on the `.lnk` file so shortcuts show the application's icon in Start Menu and on the Desktop.
- Setup installer now creates shortcuts in **three locations**:
  1. Current user Desktop
  2. Current user Start Menu → `Programs\USB Speed Test & Monitor\`
  3. All Users Start Menu (`ProgramData`) → `Programs\USB Speed Test & Monitor\` (requires admin, silently skips if insufficient permissions)

---

## [1.2.0] — 2026-06-20

### Added
- **AI Assistant Guardrails file** (`C:\ProgramData\USBSpeedTest\Guardrails.md`) — AI scope rules are now stored in an editable Markdown file on disk and loaded at query time. Administrators can update guardrails without recompiling the application.
- **Online device specs search** — When a user asks about device specifications, the AI client queries DuckDuckGo Lite for the device model and injects the web snippet into the LLM context alongside Windows PnP driver details.
- **Offline detection** — If the host machine cannot reach the internet, the AI reports back that online specification lookup is unavailable rather than silently failing.
- **Profanity filter** — Regex-based profanity detection blocks inappropriate queries and responds: *"You have used a restricted word. This query will be marked and sent for review."*
- **Clipboard copy button** — A **📋 Copy** button is appended to AI responses, allowing users to copy slowness report email templates or diagnostic summaries to the clipboard in one click.
- **Extended AI scope rules** — Explicit detection for out-of-scope requests: general email writing for unrelated projects, Python script requests for internal projects, movie/image/PDF generation, and other non-USB topics.
- **Cross-platform build system** — `build.py` and `build.sh` automatically detect Windows, Linux, or macOS and compile the appropriate deployment artefact (`.exe` + setup wizard / `.deb` package / `.dmg` disk image).
- **Offline specs fallback** — If DuckDuckGo is unreachable, the system context still enriches the LLM with local Windows PnP driver data.
- **User Guide** (`docs/User_Guide.md`) — Non-technical end-user documentation explaining every feature without requiring Python knowledge.
- **Updated README.md** — Full technical documentation covering architecture, AI chatbot, guardrails, build system, and configuration.

### Changed
- AI Assistant now dynamically queries connected device driver details (provider, version, date) and passes them as structured context to the LLM on every query.
- HTTP timeout for AI requests increased from default to **300 seconds** to accommodate slow local LLM hardware.

### Fixed
- Application logs now written to `C:\ProgramData\USBSpeedTest\logs\app.log` via a `Tee` class that writes to both stdout and the log file simultaneously.
- PyInstaller portable mode path resolution corrected so the GUI directory (`gui/`) is located relative to `sys._MEIPASS` when running as a bundled executable.

---

## [1.1.0] — 2026-06-20

### Added
- **AI Chatbot Assistant** — Full LLM integration supporting:
  - **Ollama** (local, default)
  - **Gemini** (Google)
  - **Claude** (Anthropic)
  - **OpenAI** (GPT-4)
  - **DeepSeek**
  - **Groq**
  - **Custom OpenAI-compatible endpoints** (e.g. LM Studio)
- **Configuration persistence** — Settings saved at `C:\ProgramData\USBSpeedTest\config.json` on Windows (survives uninstall/reinstall). On macOS/Linux, config is stored at the platform-appropriate user data directory.
- **Export Configuration** button — Under Application Settings, exports the full config as a `.cfg` file with filename format: `USBSpeedTest_<MachineName>_<ddMMMyyyy>_<HHmm>_<timezone>.cfg`.
- **Comparisons directory** — Side-by-side comparison HTML reports are now saved to `C:\ProgramData\USBSpeedTest\comparisions\` (separate from test reports). The Reports tab scans both directories.
- **Open Comparisons Folder** button — One-click access to the comparisons directory from the UI.
- **Setup Installer** (`UBSSpeedtest_setup.exe`) — Standalone GUI wizard that copies `USBSpeedTest.exe` to `C:\ProgramData\USBSpeedTest\`, creates Desktop and Start Menu shortcuts, and optionally launches the app immediately. Verbose installation logs saved to `C:\ProgramData\USBSpeedTest\setup_install.log`.
- **Windows Driver Enrichment** — USB storage devices and peripherals now include `driver_provider`, `driver_version`, and `driver_date` fields retrieved from `Win32_PnPSignedDriver` via PowerShell.
- **Application Info API** — `get_app_info()` backend method exposes version, platform, data directory, and Python version to the frontend.
- **Session ID** — Each application session is tagged with a unique ID (`session-YYYYMMDD-xxxxxx`) for log correlation.

### Changed
- Config directory on Windows hard-coded to `C:\ProgramData\USBSpeedTest` (overrides portable-mode detection) to ensure settings persist across reinstalls.
- `ensure_directories()` now also creates the `comparisions/` subfolder and writes the default `Guardrails.md` if it does not exist.
- `build.bat` updated to call `build.py` (cross-platform Python build controller).

### Fixed
- Setup installer button layout fixed — Install and Cancel buttons were clipped off-screen on lower resolution displays.
- Setup installer subprocess launch fixed — `Popen` call with `DETACHED_PROCESS` was crashing due to incorrect parameter (WinError 87). Resolved by using `subprocess.Popen([str(self.dest_exe)], creationflags=subprocess.DETACHED_PROCESS)`.
- Installation path corrected from `UBSSpeedTest` to `USBSpeedTest` across all references.

---

## [1.0.0] — 2026-06-20

### Added
- **Devices Tab** — Enumerates all connected USB peripherals (storage drives, audio devices, cameras, keyboards, mice, and other peripherals). Displays device class, removability, mount point, and vendor information. Uses PowerShell `Get-Disk`/`Get-PnpDevice` on Windows, `diskutil` on macOS, and `lsblk`/`lsusb` on Linux.
- **Storage Tab** — Visual disk space analysis with high-contrast progress bars showing used vs. free capacity and file system type for each mounted USB volume.
- **Speed Test Tab** — Sequential write and read benchmarks with configurable file sizes (20 MB, 50 MB, 100 MB, 250 MB). Uses `os.fsync` cache flushing to ensure hardware-accurate (not RAM-cached) results. Real-time progress with live speed display.
- **Comparison Tab** — Select multiple previous test runs and generate a side-by-side HTML performance matrix comparing write speed, read speed, and latency across devices.
- **Reports Tab** — Lists all saved HTML benchmark reports with timestamps. Click any entry to open the detailed report in the system browser.
- **HTML Reports** — Rich, self-contained HTML benchmark reports including device metadata, sequential throughput results, and formatted tables.
- **Background Monitoring Service** — Runs as a lightweight background thread checking USB disk space every 60 seconds (configurable). Fires native Windows/macOS/Linux system toast notifications when a connected drive falls below 10% free space (configurable threshold).
- **System Tray Integration** — Application minimises to the system tray with a context menu exposing Show Window and Exit App actions.
- **Application Settings** — Configurable UI for monitoring interval, disk threshold, AI provider details, and default test file size. Settings persisted to `config.json`.
- **Premium Dark UI** — Glassmorphic dark-mode design with purple accent colour, smooth tab transitions, animated loading states, and responsive grid layouts.
- **Cross-platform support** — Functional on Windows 10/11, macOS (Monterey+), and Ubuntu/Debian Linux.

---

[1.3.0]: https://github.com/pellurisrinath/USBSpeedTester/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/pellurisrinath/USBSpeedTester/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/pellurisrinath/USBSpeedTester/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pellurisrinath/USBSpeedTester/releases/tag/v1.0.0
