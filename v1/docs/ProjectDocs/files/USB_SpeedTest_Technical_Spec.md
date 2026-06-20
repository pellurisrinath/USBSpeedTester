# USB Speed Test and Monitoring Application
## Comprehensive Technical Specification & Implementation Guide

**Version**: 1.0  
**Last Updated**: June 2026  
**Target Platforms**: Windows, macOS, Linux  
**Application Type**: Cross-Platform Standalone Desktop Application

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Technical Stack](#technical-stack)
4. [System Requirements](#system-requirements)
5. [Project Structure](#project-structure)
6. [Core Modules](#core-modules)
7. [Data Models](#data-models)
8. [API Specifications](#api-specifications)
9. [Configuration & Paths](#configuration--paths)
10. [Security Considerations](#security-considerations)
11. [Performance Metrics](#performance-metrics)

---

## Executive Summary

The USB Speed Test and Monitoring Application is a cross-platform desktop utility designed to:

- **Enumerate** all connected USB devices (storage and non-storage peripherals)
- **Analyze** disk space usage with detailed statistics
- **Benchmark** read/write speeds on USB storage devices
- **Generate** professional HTML reports and comparison analyses
- **Monitor** background disk space and issue notifications
- **Support** filtering and sorting of devices by type

The application uses a **Python backend** with **PyWebView** for the frontend, ensuring a consistent user experience across Windows, macOS, and Linux platforms.

---

## Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│         (HTML5 + CSS + JavaScript via PyWebView)            │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ (JavaScript Bridge API)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API Layer (Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Device Detect│  │ Speed Test   │  │ Report Gen   │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────┐       │
│  │      Platform-Specific Drivers (Win/Mac/Linux)   │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ (System Calls)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Operating System Layer                      │
│  (WMI, diskutil, /sys/class/block, lsblk, etc.)            │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
START
  │
  ├─► Load Application (main.py)
  │    ├─► Initialize PyWebView
  │    ├─► Launch Background Monitor Service
  │    └─► Display UI
  │
  ├─► User Action: List USB Devices
  │    ├─► usb_detector.py → Platform-specific enumeration
  │    ├─► Filter by type (Storage/Audio/Camera/etc)
  │    └─► Return to Frontend (JSON)
  │
  ├─► User Action: Run Speed Test
  │    ├─► speed_test.py → Create temp files
  │    ├─► Write test (50-100MB chunks)
  │    ├─► Read test (same chunks)
  │    ├─► Calculate MB/s
  │    ├─► Clean up temp files
  │    └─► Return results to Frontend
  │
  ├─► User Action: Generate Report
  │    ├─► report_generator.py
  │    ├─► Compile device info + test results
  │    ├─► Generate HTML with charts
  │    └─► Save to C:\ProgramData\UBSSpeedTest\ (Windows)
  │
  └─► Background Monitor (runs continuously)
       ├─► Poll disk space every 60 seconds
       ├─► Check if free space < 10%
       └─► Trigger notification if threshold breached
```

---

## Technical Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Core Language | Python | 3.9+ | Main application logic |
| UI Rendering | PyWebView | 4.0+ | Embed web UI in desktop app |
| System Info | psutil | 5.8+ | Disk space, CPU, memory stats |
| USB Detection | pyudev (Linux), wmi (Windows) | Latest | Device enumeration |
| Notifications | plyer / OS-native APIs | 2.1+ | System notifications |
| System Tray | pystray | 0.17+ | Background tray icon |
| File I/O | Python stdlib | Built-in | Temp file handling |
| JSON | Python stdlib | Built-in | API serialization |
| HTML Reports | Jinja2 | 3.0+ | Template-based report generation |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Markup | HTML5 | Semantic structure |
| Styling | CSS3 | Glassmorphism, animations, dark theme |
| Interactivity | Vanilla JavaScript | DOM manipulation, event handling |
| Charts | Chart.js | Visual storage/speed representations |
| Icons | FontAwesome / Custom SVG | UI elements |

### Packaging & Distribution

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Build Tool | PyInstaller | Standalone executable creation |
| Code Signing | (Optional) signtool (Windows), codesign (macOS) | Security & trust |
| Installer (Optional) | NSIS / InnoSetup (Windows), DMG (macOS), AppImage (Linux) | Distribution packaging |

---

## System Requirements

### Minimum Requirements

#### Windows
- OS: Windows 10 or later (build 19041+)
- Processor: Intel Pentium or equivalent (2 GHz+)
- RAM: 512 MB
- Disk Space: 100 MB
- Permissions: Local administrator or standard user

#### macOS
- OS: macOS 10.13 or later
- Processor: Intel or Apple Silicon (M1+)
- RAM: 512 MB
- Disk Space: 100 MB
- Permissions: Standard user (with Accessibility permission for tray icon)

#### Linux
- OS: Ubuntu 18.04+, Debian 10+, CentOS 7+, or equivalent
- Processor: Intel or ARM (ARMv7+)
- RAM: 512 MB
- Disk Space: 100 MB
- Permissions: Standard user (read access to /sys/class/block)

### Recommended Requirements

- RAM: 2 GB+
- Disk Space: 500 MB (with storage for reports)
- Display: 1920x1080 or higher

### Runtime Dependencies

```
Python 3.9+
Required Packages:
  - pywebview==4.x
  - psutil==5.8+
  - pyudev==0.22+ (Linux)
  - pystray==0.17+
  - plyer==2.1+
  - Jinja2==3.0+
  - requests==2.28+ (for future cloud features)
  
Optional Packages:
  - pyinstaller==5.5+ (for packaging)
  - wheel==0.37+ (for distribution)
```

---

## Project Structure

```
USBSpeedTest/
│
├── src/
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration & constants
│   ├── api.py                     # Flask/PyWebView API endpoints
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── usb_detector.py        # USB device enumeration
│   │   ├── speed_test.py          # Benchmark logic
│   │   ├── report_generator.py    # HTML report creation
│   │   ├── monitor_service.py     # Background monitoring & tray
│   │   └── platform_utils.py      # Cross-platform utilities
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Logging configuration
│       ├── file_handler.py        # File I/O operations
│       └── validators.py          # Input validation
│
├── gui/
│   ├── index.html                 # Main UI
│   ├── style.css                  # Styling (glassmorphism theme)
│   ├── app.js                     # Frontend logic
│   ├── templates/
│   │   ├── device_card.html       # Device component template
│   │   └── report_template.html   # HTML report template
│   └── assets/
│       ├── icons/
│       ├── fonts/
│       └── images/
│
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package configuration
├── pyinstaller.spec              # PyInstaller build specification
│
├── tests/
│   ├── unit/
│   │   ├── test_usb_detector.py
│   │   ├── test_speed_test.py
│   │   └── test_report_generator.py
│   ├── integration/
│   │   └── test_api.py
│   └── conftest.py               # Pytest fixtures
│
├── docs/
│   ├── ARCHITECTURE.md            # Detailed architecture
│   ├── INSTALLATION.md            # Installation guide
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment & packaging
│   └── TROUBLESHOOTING.md         # Common issues & fixes
│
├── scripts/
│   ├── build_windows.bat          # Windows build script
│   ├── build_macos.sh             # macOS build script
│   ├── build_linux.sh             # Linux build script
│   └── sign_releases.sh           # Code signing script
│
├── .github/
│   └── workflows/
│       └── build-release.yml      # GitHub Actions CI/CD
│
└── README.md                      # Project overview
```

---

## Core Modules

### 1. main.py - Application Entry Point

**Responsibilities:**
- Initialize PyWebView application
- Register API endpoints
- Launch background monitoring service
- Handle application lifecycle (startup/shutdown)
- Coordinate module interactions

**Key Functions:**
```python
def initialize_app() -> PyWebView.api
    """Setup application and return API object"""

def start_background_monitor()
    """Launch background monitoring service"""

def on_app_close()
    """Cleanup resources and exit gracefully"""

def run()
    """Main application loop"""
```

### 2. usb_detector.py - Device Enumeration

**Responsibilities:**
- Detect all connected USB devices
- Classify devices (Storage, Audio, Camera, Generic, etc.)
- Retrieve device metadata (Name, Vendor, Serial, Mount Point)
- Provide filtered device lists

**Key Functions:**
```python
class DeviceDetector:
    def detect_all_devices() -> List[Device]
    def detect_storage_devices() -> List[StorageDevice]
    def detect_peripheral_devices() -> List[PeripheralDevice]
    def get_device_type(device) -> DeviceType
    def filter_by_type(devices, type) -> List[Device]
    def get_device_info(device_path) -> Dict
```

**Device Model:**
```python
@dataclass
class Device:
    name: str
    vendor: str
    product_id: str
    vendor_id: str
    serial: str
    bus_type: str  # USB, SATA, NVMe, etc.
    device_type: str  # Storage, Audio, Camera, etc.
    mount_point: Optional[str]
    device_path: str
    is_removable: bool
    added_timestamp: float
```

### 3. speed_test.py - Benchmark Module

**Responsibilities:**
- Perform read/write speed tests on USB devices
- Create temporary test files
- Calculate throughput (MB/s)
- Handle errors and cleanup
- Support configurable test sizes

**Key Functions:**
```python
class SpeedTester:
    def run_speed_test(device_path: str, test_size_mb: int = 100) -> TestResult
    def write_test(device_path: str, file_size_mb: int) -> Tuple[float, float]
    def read_test(device_path: str, file_path: str) -> Tuple[float, float]
    def cleanup_temp_files(device_path: str)
    def calculate_speed(bytes_written: int, duration_sec: float) -> float
```

**Test Result Model:**
```python
@dataclass
class TestResult:
    device_name: str
    device_path: str
    mount_point: str
    file_system: str
    test_size_mb: int
    write_speed_mbps: float
    read_speed_mbps: float
    write_duration_sec: float
    read_duration_sec: float
    timestamp: datetime
    total_space_gb: float
    used_space_gb: float
    free_space_gb: float
    test_id: str  # UUID for comparison tracking
```

### 4. report_generator.py - Report Creation

**Responsibilities:**
- Generate HTML reports from test results
- Create comparison reports
- Apply styling and templates
- Save reports to disk

**Key Functions:**
```python
class ReportGenerator:
    def generate_device_report(device_info: Dict, test_result: TestResult) -> str
    def generate_comparison_report(test_results: List[TestResult]) -> str
    def save_report(html_content: str, report_type: str) -> str
    def render_template(template_name: str, context: Dict) -> str
```

### 5. monitor_service.py - Background Monitoring

**Responsibilities:**
- Monitor disk space periodically
- Trigger notifications when thresholds breached
- Manage system tray icon
- Handle service lifecycle

**Key Functions:**
```python
class MonitorService:
    def start()
    def stop()
    def check_disk_space() -> Dict[str, float]
    def is_low_disk_space(free_percent: float) -> bool
    def send_notification(title: str, message: str)
    def on_tray_icon_clicked(icon, item)
```

### 6. platform_utils.py - Cross-Platform Utilities

**Responsibilities:**
- Abstract platform-specific logic
- Provide unified interface for system calls
- Handle Windows/macOS/Linux differences

**Key Functions:**
```python
def get_platform() -> str  # 'windows', 'darwin', 'linux'
def get_app_data_dir() -> Path
def get_mount_points(device_path: str) -> List[str]
def run_platform_command(cmd: List[str]) -> str
def get_usb_devices_platform_specific() -> List[Dict]
def open_file_explorer(path: str)
```

---

## Data Models

### Device Types Enumeration

```python
class DeviceType(Enum):
    STORAGE = "STORAGE"           # USB drives, external HDDs
    AUDIO = "AUDIO"               # Speakers, headphones, mics
    CAMERA = "CAMERA"             # Cameras, webcams
    PRINTER = "PRINTER"           # Printers, scanners
    INPUT = "INPUT"               # Keyboards, mice, gamepads
    HID = "HID"                   # Human Interface Devices
    NETWORK = "NETWORK"           # Network adapters
    MOBILE = "MOBILE"             # Phones, tablets
    OTHER = "OTHER"               # Unclassified
    GENERIC = "GENERIC"           # Generic devices
```

### Device Information Structure

```python
@dataclass
class StorageDevice(Device):
    total_space: int           # bytes
    used_space: int            # bytes
    free_space: int            # bytes
    file_system: str           # NTFS, FAT32, ext4, APFS, etc.
    is_mounted: bool
    mount_point: str
    block_size: int
    
@dataclass
class PeripheralDevice(Device):
    device_class: str
    device_subclass: str
    protocol: str
    speed: str                 # USB 2.0, 3.0, 3.1, Thunderbolt, etc.
```

### Test Session Model

```python
@dataclass
class TestSession:
    session_id: str            # UUID
    start_time: datetime
    end_time: Optional[datetime]
    test_results: List[TestResult]
    comparison_generated: bool
    comparison_report_path: Optional[str]
```

---

## API Specifications

### Python-to-JavaScript Bridge (PyWebView API)

All functions return JSON-serializable data.

#### Device Management APIs

```python
# Get all connected devices
@api.expose
async def get_all_devices() -> Dict
    """Returns: {
        "success": bool,
        "devices": [
            {
                "id": "usb-001",
                "name": "Kingston DataTraveler",
                "vendor": "Kingston",
                "type": "STORAGE",
                "is_removable": true,
                "mount_point": "/media/user/Kingston"
            }
        ]
    }"""

# Get storage devices only
@api.expose
async def get_storage_devices() -> Dict
    """Returns list of storage devices with space info"""

# Get peripheral devices only
@api.expose
async def get_peripheral_devices() -> Dict
    """Returns list of non-storage devices"""

# Get devices filtered by type
@api.expose
async def get_devices_by_type(device_type: str) -> Dict
    """Parameters: device_type in [STORAGE, AUDIO, CAMERA, etc.]"""

# Get detailed device information
@api.expose
async def get_device_details(device_id: str) -> Dict
    """Returns comprehensive device metadata"""
```

#### Storage Analysis APIs

```python
# Get space info for a device
@api.expose
async def get_space_info(device_path: str) -> Dict
    """Returns: {
        "total_gb": 32.0,
        "used_gb": 15.5,
        "free_gb": 16.5,
        "percent_used": 48.4,
        "file_system": "NTFS"
    }"""
```

#### Speed Test APIs

```python
# Run speed test on a device
@api.expose
async def run_speed_test(device_path: str, test_size_mb: int = 100) -> Dict
    """Returns: {
        "success": bool,
        "test_id": "test-001",
        "device_name": "Kingston DataTraveler",
        "write_speed_mbps": 85.5,
        "read_speed_mbps": 92.3,
        "test_size_mb": 100,
        "duration_sec": 2.5,
        "timestamp": "2024-06-20T14:30:00Z"
    }"""

# Get speed test history
@api.expose
async def get_test_history() -> Dict
    """Returns list of all tests performed in current session"""

# Cancel running test
@api.expose
async def cancel_speed_test() -> Dict
```

#### Report Generation APIs

```python
# Generate device report
@api.expose
async def generate_device_report(test_id: str) -> Dict
    """Generates and saves HTML report, returns path"""

# Generate comparison report
@api.expose
async def generate_comparison_report(test_ids: List[str]) -> Dict
    """Generates comparison report for multiple tests"""

# Get report list
@api.expose
async def get_reports_list() -> Dict
    """Returns list of generated reports with metadata"""

# Open report file
@api.expose
async def open_report(report_path: str) -> bool
    """Opens report in default browser/viewer"""
```

#### System APIs

```python
# Get application info
@api.expose
async def get_app_info() -> Dict
    """Returns app version, paths, configuration"""

# Get system info
@api.expose
async def get_system_info() -> Dict
    """Returns OS, Python version, installed libraries"""

# Get configuration
@api.expose
async def get_config() -> Dict

# Update configuration
@api.expose
async def update_config(config_dict: Dict) -> bool

# Open file in explorer
@api.expose
async def open_path(path: str) -> bool
```

---

## Configuration & Paths

### Application Paths

```python
# Windows
WINDOWS_DATA_DIR = "C:\\ProgramData\\UBSSpeedTest"
WINDOWS_REPORTS_DIR = "C:\\ProgramData\\UBSSpeedTest\\reports"
WINDOWS_LOGS_DIR = "C:\\ProgramData\\UBSSpeedTest\\logs"

# macOS
MACOS_DATA_DIR = "~/Library/Application Support/USBSpeedTest"
MACOS_REPORTS_DIR = "~/Library/Application Support/USBSpeedTest/reports"
MACOS_LOGS_DIR = "~/Library/Application Support/USBSpeedTest/logs"

# Linux
LINUX_DATA_DIR = "~/.local/share/usb-speedtest"
LINUX_REPORTS_DIR = "~/.local/share/usb-speedtest/reports"
LINUX_LOGS_DIR = "~/.local/share/usb-speedtest/logs"
```

### Configuration File (config.json)

```json
{
    "app": {
        "version": "1.0.0",
        "check_updates": true
    },
    "speed_test": {
        "default_test_size_mb": 100,
        "chunk_size_mb": 10,
        "timeout_seconds": 300,
        "enable_write_test": true,
        "enable_read_test": true
    },
    "monitoring": {
        "enabled": true,
        "check_interval_seconds": 60,
        "low_disk_threshold_percent": 10,
        "enable_notifications": true,
        "ignored_devices": []
    },
    "ui": {
        "theme": "dark",
        "auto_refresh_interval_ms": 5000,
        "show_all_devices": true
    },
    "reporting": {
        "auto_save": true,
        "include_charts": true,
        "include_device_history": true
    }
}
```

---

## Security Considerations

### Input Validation

```python
# All user inputs must be validated
- Device paths: Whitelist known safe patterns
- Test sizes: Range validation (10-1000 MB)
- File operations: Use pathlib for path safety
- Command execution: Never use shell=True
```

### Permissions

```
Windows: 
  - Temp file creation in device root (may require elevation)
  - Notification/tray icon access (standard user OK)
  - Registry read (for WMI queries)

macOS:
  - Temp file creation (standard user)
  - Accessibility permission for tray (optional)
  - File system access (standard user)

Linux:
  - Read /sys/class/block (standard user)
  - Read /proc/mounts (standard user)
  - Temp file creation (standard user)
```

### Data Privacy

```
- No telemetry collection (unless explicitly enabled)
- Reports saved locally only
- No cloud upload without user consent
- No personal data collection
- Sensitive paths masked in logs
```

### Code Signing & Distribution

```
Windows:
  - Sign executable with EV certificate (optional)
  - Use NSIS installer with digital signature
  
macOS:
  - Code sign application bundle
  - Notarize with Apple (required for Big Sur+)
  - Create .dmg with code signature
  
Linux:
  - GPG sign AppImage or tarball
  - Provide SHA256 checksums
```

---

## Performance Metrics

### Expected Performance

| Operation | Typical Duration | Notes |
|-----------|------------------|-------|
| List USB devices | 100-500 ms | Depends on device count |
| Speed test (100MB) | 2-10 seconds | Variable by device speed |
| Generate HTML report | 50-200 ms | With charts and formatting |
| Comparison report (5 devices) | 100-300 ms | Minimal processing |
| Application startup | 1-3 seconds | PyWebView initialization |

### Resource Usage

```
Memory (idle):
  - Windows: 80-150 MB
  - macOS: 100-180 MB
  - Linux: 70-130 MB

Memory (during speed test):
  - Peak: +50-100 MB for test file buffering

Disk I/O:
  - Write test: Contiguous write of test_size
  - Read test: Sequential read of same size
  - Cleanup: Immediate deletion of test file

CPU:
  - Device enumeration: <5% (brief spike)
  - Speed test: 10-30% (I/O bound, not CPU bound)
  - Report generation: <5%
```

### Optimization Strategies

```
1. Cache device lists for 2-5 seconds
2. Use async/await for long-running operations
3. Stream large file reads/writes with chunking
4. Lazy-load UI components
5. Minimize notification frequency
6. Use efficient JSON serialization
```

---

## Next Steps

1. Review and approve this specification
2. Set up development environment
3. Implement core modules (start with usb_detector.py)
4. Build frontend UI components
5. Integrate PyWebView API bridge
6. Test on all target platforms
7. Create installers and distribution packages

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | June 2026 | DevTeam | Initial specification |

---

**End of Technical Specification**
