# API & Frontend Implementation Guide
## USB Speed Test and Monitoring Application

---

## Table of Contents

1. [API Documentation](#api-documentation)
2. [Frontend Architecture](#frontend-architecture)
3. [HTML Structure](#html-structure)
4. [CSS Styling & Theme](#css-styling--theme)
5. [JavaScript Implementation](#javascript-implementation)
6. [Component Examples](#component-examples)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)

---

## API Documentation

### API Overview

The backend exposes a Python API through PyWebView's JavaScript bridge. All API calls return JSON responses with standardized error handling.

**Response Format:**
```json
{
    "success": true,
    "data": {},
    "error": null,
    "timestamp": "2024-06-20T14:30:00Z"
}
```

### Device Management API

#### 1. Get All Connected Devices

**Endpoint:** `api.get_all_devices()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "total_devices": 3,
        "devices": [
            {
                "id": "usb-001",
                "name": "Kingston DataTraveler 3.0",
                "vendor": "Kingston",
                "product_id": "1234",
                "vendor_id": "0951",
                "serial": "ABC123XYZ",
                "device_type": "STORAGE",
                "bus_type": "USB",
                "is_removable": true,
                "mount_point": "D:",
                "device_path": "\\\\.\\PhysicalDrive2"
            },
            {
                "id": "usb-002",
                "name": "Logitech USB Headset",
                "vendor": "Logitech",
                "product_id": "5678",
                "vendor_id": "046D",
                "device_type": "AUDIO",
                "bus_type": "USB",
                "is_removable": true,
                "mount_point": null
            }
        ]
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "data": null,
    "error": "Failed to enumerate USB devices: [error details]"
}
```

#### 2. Get Storage Devices Only

**Endpoint:** `api.get_storage_devices()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "total_storage_devices": 2,
        "devices": [
            {
                "id": "usb-001",
                "name": "Kingston DataTraveler",
                "mount_point": "D:",
                "device_type": "STORAGE",
                "file_system": "NTFS",
                "total_space_gb": 32.0,
                "used_space_gb": 15.5,
                "free_space_gb": 16.5,
                "percent_used": 48.4,
                "is_mounted": true
            }
        ]
    }
}
```

#### 3. Get Peripheral Devices Only

**Endpoint:** `api.get_peripheral_devices()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "total_peripheral_devices": 2,
        "devices": [
            {
                "id": "usb-002",
                "name": "Logitech USB Headset",
                "vendor": "Logitech",
                "device_type": "AUDIO",
                "speed": "USB 2.0",
                "protocol": "Audio"
            }
        ]
    }
}
```

#### 4. Get Devices by Type

**Endpoint:** `api.get_devices_by_type(device_type)`

**Parameters:**
- `device_type` (string): One of `STORAGE`, `AUDIO`, `CAMERA`, `PRINTER`, `INPUT`, `MOBILE`, `GENERIC`, `OTHER`

**Response:**
```json
{
    "success": true,
    "data": {
        "device_type": "AUDIO",
        "count": 1,
        "devices": [...]
    }
}
```

#### 5. Get Device Details

**Endpoint:** `api.get_device_details(device_id)`

**Parameters:**
- `device_id` (string): Unique device identifier (e.g., "usb-001")

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "usb-001",
        "name": "Kingston DataTraveler 3.0",
        "vendor": "Kingston",
        "vendor_id": "0951",
        "product_id": "1234",
        "serial": "ABC123XYZ",
        "device_type": "STORAGE",
        "bus_type": "USB",
        "speed": "USB 3.0",
        "is_removable": true,
        "is_mounted": true,
        "mount_point": "D:",
        "device_path": "\\\\.\\PhysicalDrive2",
        "file_system": "NTFS",
        "total_space_bytes": 34359738368,
        "total_space_gb": 32.0,
        "used_space_bytes": 16696320819,
        "used_space_gb": 15.5,
        "free_space_bytes": 17663417549,
        "free_space_gb": 16.5,
        "percent_used": 48.4
    }
}
```

---

### Storage Analysis API

#### Get Space Information

**Endpoint:** `api.get_space_info(device_id)`

**Parameters:**
- `device_id` (string): Device identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "device_id": "usb-001",
        "device_name": "Kingston DataTraveler",
        "total_bytes": 34359738368,
        "total_gb": 32.0,
        "used_bytes": 16696320819,
        "used_gb": 15.5,
        "free_bytes": 17663417549,
        "free_gb": 16.5,
        "percent_used": 48.4,
        "percent_free": 51.6,
        "file_system": "NTFS",
        "mount_point": "D:"
    }
}
```

---

### Speed Test API

#### Run Speed Test

**Endpoint:** `api.run_speed_test(device_id, test_size_mb=100)`

**Parameters:**
- `device_id` (string): Device identifier
- `test_size_mb` (integer, optional): Test file size in MB (default: 100)

**Progress Events:** (via WebSocket or polling)
```json
{
    "type": "progress",
    "status": "writing",
    "percent": 45,
    "current_mb": 45,
    "total_mb": 100
}
```

**Completion Response:**
```json
{
    "success": true,
    "data": {
        "test_id": "test-2024-06-20-143000-abc123",
        "device_id": "usb-001",
        "device_name": "Kingston DataTraveler",
        "device_path": "D:",
        "file_system": "NTFS",
        "test_size_mb": 100,
        "test_duration_sec": 2.45,
        "write_speed_mbps": 85.5,
        "read_speed_mbps": 92.3,
        "write_duration_sec": 1.17,
        "read_duration_sec": 1.08,
        "timestamp": "2024-06-20T14:30:00Z",
        "space_info": {
            "total_space_gb": 32.0,
            "used_space_gb": 15.5,
            "free_space_gb": 16.5,
            "percent_used": 48.4
        }
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "data": null,
    "error": "Speed test failed: Device not found or access denied"
}
```

#### Get Test History

**Endpoint:** `api.get_test_history()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "session-2024-06-20-001",
        "session_start_time": "2024-06-20T13:00:00Z",
        "total_tests": 3,
        "tests": [
            {
                "test_id": "test-2024-06-20-143000-abc123",
                "device_name": "Kingston DataTraveler",
                "device_id": "usb-001",
                "write_speed_mbps": 85.5,
                "read_speed_mbps": 92.3,
                "timestamp": "2024-06-20T14:30:00Z"
            }
        ]
    }
}
```

#### Cancel Speed Test

**Endpoint:** `api.cancel_speed_test()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Speed test cancelled successfully"
    }
}
```

---

### Report Generation API

#### Generate Device Report

**Endpoint:** `api.generate_device_report(test_id)`

**Parameters:**
- `test_id` (string): Test identifier from speed test

**Response:**
```json
{
    "success": true,
    "data": {
        "report_id": "report-2024-06-20-143000-abc123",
        "report_path": "C:\\ProgramData\\UBSSpeedTest\\reports\\report_2024-06-20_14-30-00.html",
        "file_size_bytes": 125000,
        "generated_timestamp": "2024-06-20T14:31:00Z",
        "device_name": "Kingston DataTraveler",
        "test_date": "2024-06-20T14:30:00Z"
    }
}
```

#### Generate Comparison Report

**Endpoint:** `api.generate_comparison_report(test_ids)`

**Parameters:**
- `test_ids` (array of strings): Array of test IDs to compare

**Response:**
```json
{
    "success": true,
    "data": {
        "report_id": "compare-2024-06-20-143000-xyz789",
        "report_path": "C:\\ProgramData\\UBSSpeedTest\\reports\\compare_2024-06-20_14-30-00.html",
        "file_size_bytes": 250000,
        "generated_timestamp": "2024-06-20T14:32:00Z",
        "compared_tests_count": 2,
        "devices_compared": [
            "Kingston DataTraveler",
            "SanDisk Extreme"
        ]
    }
}
```

#### Get Reports List

**Endpoint:** `api.get_reports_list(limit=50)`

**Parameters:**
- `limit` (integer, optional): Maximum reports to return (default: 50)

**Response:**
```json
{
    "success": true,
    "data": {
        "total_reports": 5,
        "reports": [
            {
                "report_id": "report-2024-06-20-143000-abc123",
                "report_type": "device",
                "file_name": "report_2024-06-20_14-30-00.html",
                "file_path": "C:\\ProgramData\\UBSSpeedTest\\reports\\report_2024-06-20_14-30-00.html",
                "file_size_bytes": 125000,
                "created_timestamp": "2024-06-20T14:31:00Z",
                "device_name": "Kingston DataTraveler"
            }
        ]
    }
}
```

#### Open Report

**Endpoint:** `api.open_report(report_path)`

**Parameters:**
- `report_path` (string): Full path to report file

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Report opened in default browser"
    }
}
```

---

### System API

#### Get Application Info

**Endpoint:** `api.get_app_info()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "app_name": "USB Speed Test",
        "app_version": "1.0.0",
        "build_number": "20240620",
        "copyright": "2024",
        "platform": "windows",
        "data_directory": "C:\\ProgramData\\UBSSpeedTest",
        "config_file": "C:\\ProgramData\\UBSSpeedTest\\config.json"
    }
}
```

#### Get System Info

**Endpoint:** `api.get_system_info()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "os_name": "Windows",
        "os_version": "10",
        "os_build": "19045",
        "python_version": "3.9.13",
        "pywebview_version": "4.0",
        "processor_count": 8,
        "total_memory_gb": 16,
        "available_memory_gb": 8
    }
}
```

#### Get Configuration

**Endpoint:** `api.get_config()`

**Parameters:** None

**Response:**
```json
{
    "success": true,
    "data": {
        "speed_test": {
            "default_test_size_mb": 100,
            "chunk_size_mb": 10,
            "timeout_seconds": 300
        },
        "monitoring": {
            "enabled": true,
            "check_interval_seconds": 60,
            "low_disk_threshold_percent": 10
        },
        "ui": {
            "theme": "dark",
            "auto_refresh_interval_ms": 5000
        }
    }
}
```

#### Update Configuration

**Endpoint:** `api.update_config(config_dict)`

**Parameters:**
- `config_dict` (object): Configuration to update

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Configuration updated successfully"
    }
}
```

#### Open Path in File Explorer

**Endpoint:** `api.open_path(path)`

**Parameters:**
- `path` (string): File or directory path to open

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "File explorer opened"
    }
}
```

---

## Frontend Architecture

### Directory Structure

```
gui/
├── index.html              # Main entry point
├── style.css               # Global styling
├── app.js                  # Main application controller
├── components/
│   ├── device-list.js      # Device listing component
│   ├── storage-panel.js    # Storage analysis panel
│   ├── speed-test-panel.js # Speed test interface
│   ├── comparison-panel.js # Comparison feature
│   ├── report-panel.js     # Report generation
│   └── settings-panel.js   # Settings/config
├── templates/
│   ├── device-card.html    # Device card template
│   ├── test-result.html    # Test result template
│   └── comparison-table.html # Comparison table template
├── assets/
│   ├── icons/
│   │   ├── device-icons.svg
│   │   ├── action-icons.svg
│   │   └── chart-icons.svg
│   ├── fonts/
│   │   ├── outfit.woff2
│   │   └── inter.woff2
│   └── images/
│       ├── logo.png
│       └── bg-pattern.png
└── styles/
    ├── variables.css       # CSS custom properties
    ├── animations.css      # Global animations
    └── responsive.css      # Media queries
```

### Component Communication

```
┌─────────────────────────────────────┐
│      index.html (main layout)        │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐         ┌────▼──────┐
   │ app.js   │         │ style.css  │
   │ (logic)  │         │ (styling)  │
   └────┬─────┘         └────────────┘
        │
 ┌──────┼───────────────────┐
 │      │                   │
┌▼──────▼─┐  ┌──────────┐  ┌▼─────────┐
│Components│  │ API Call │  │ Templates│
│(*.js)    │  │  Bridge  │  │(*.html)  │
└──────────┘  └──────────┘  └──────────┘
                    │
            ┌───────▼────────┐
            │  Python Backend│
            │  (PyWebView)   │
            └────────────────┘
```

---

## HTML Structure

### index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="USB Speed Test and Device Monitor">
    <meta name="theme-color" content="#1a1a2e">
    
    <title>USB Speed Test & Monitor</title>
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="styles/variables.css">
    <link rel="stylesheet" href="styles/animations.css">
    <link rel="stylesheet" href="styles/responsive.css">
    
    <!-- Chart.js for visualizations -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    
    <!-- FontAwesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div id="app" class="app-container">
        
        <!-- Header -->
        <header class="app-header">
            <div class="header-content">
                <div class="header-left">
                    <h1 class="app-title">
                        <i class="fas fa-usb"></i> USB Speed Test
                    </h1>
                    <p class="app-subtitle">Device Monitor & Benchmark</p>
                </div>
                <div class="header-right">
                    <div class="header-actions">
                        <button id="refreshBtn" class="btn btn-icon" title="Refresh">
                            <i class="fas fa-sync"></i>
                        </button>
                        <button id="settingsBtn" class="btn btn-icon" title="Settings">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="app-main">
            
            <!-- Navigation Tabs -->
            <nav class="tab-navigation">
                <button class="tab-button active" data-tab="devices">
                    <i class="fas fa-list"></i> Devices
                </button>
                <button class="tab-button" data-tab="storage">
                    <i class="fas fa-hdd"></i> Storage
                </button>
                <button class="tab-button" data-tab="speedtest">
                    <i class="fas fa-tachometer-alt"></i> Speed Test
                </button>
                <button class="tab-button" data-tab="comparison">
                    <i class="fas fa-chart-bar"></i> Comparison
                </button>
                <button class="tab-button" data-tab="reports">
                    <i class="fas fa-file-pdf"></i> Reports
                </button>
            </nav>

            <!-- Tab Contents -->
            <div class="tab-contents">
                
                <!-- Devices Tab -->
                <div id="devices-tab" class="tab-content active">
                    <div class="tab-header">
                        <h2>Connected Devices</h2>
                        <div class="filter-controls">
                            <label for="deviceTypeFilter">Filter by Type:</label>
                            <select id="deviceTypeFilter">
                                <option value="">All Devices</option>
                                <option value="STORAGE">Storage</option>
                                <option value="AUDIO">Audio</option>
                                <option value="CAMERA">Camera</option>
                                <option value="PRINTER">Printer</option>
                                <option value="INPUT">Input</option>
                                <option value="MOBILE">Mobile</option>
                                <option value="GENERIC">Generic</option>
                            </select>
                        </div>
                    </div>
                    
                    <div id="devices-list" class="devices-grid">
                        <!-- Device cards injected here -->
                    </div>
                </div>

                <!-- Storage Tab -->
                <div id="storage-tab" class="tab-content">
                    <div class="tab-header">
                        <h2>Storage Analysis</h2>
                    </div>
                    
                    <div id="storage-panel" class="storage-panel">
                        <!-- Storage devices and info injected here -->
                    </div>
                </div>

                <!-- Speed Test Tab -->
                <div id="speedtest-tab" class="tab-content">
                    <div class="tab-header">
                        <h2>Speed Test</h2>
                    </div>
                    
                    <div id="speedtest-panel" class="speed-test-panel">
                        <!-- Speed test controls and results injected here -->
                    </div>
                </div>

                <!-- Comparison Tab -->
                <div id="comparison-tab" class="tab-content">
                    <div class="tab-header">
                        <h2>Test Comparison</h2>
                    </div>
                    
                    <div id="comparison-panel" class="comparison-panel">
                        <!-- Comparison table injected here -->
                    </div>
                </div>

                <!-- Reports Tab -->
                <div id="reports-tab" class="tab-content">
                    <div class="tab-header">
                        <h2>Generated Reports</h2>
                    </div>
                    
                    <div id="reports-panel" class="reports-panel">
                        <!-- Reports list injected here -->
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="app-footer">
            <div class="footer-content">
                <p class="footer-text">USB Speed Test v1.0.0</p>
                <p class="footer-text" id="statusText">Ready</p>
            </div>
        </footer>

        <!-- Settings Modal -->
        <div id="settingsModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Settings</h3>
                    <button class="modal-close" data-action="closeSettings">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body" id="settingsBody">
                    <!-- Settings form injected here -->
                </div>
            </div>
        </div>

        <!-- Progress Modal -->
        <div id="progressModal" class="modal">
            <div class="modal-content modal-progress">
                <div class="modal-body">
                    <h4 id="progressTitle">Running Speed Test</h4>
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill" style="width: 0%"></div>
                    </div>
                    <p id="progressText">0%</p>
                    <button id="cancelBtn" class="btn btn-danger">Cancel</button>
                </div>
            </div>
        </div>

        <!-- Toast Notification Container -->
        <div id="toastContainer" class="toast-container"></div>
    </div>

    <!-- JavaScript -->
    <script src="app.js"></script>
    <script src="components/device-list.js"></script>
    <script src="components/storage-panel.js"></script>
    <script src="components/speed-test-panel.js"></script>
    <script src="components/comparison-panel.js"></script>
    <script src="components/report-panel.js"></script>
</body>
</html>
```

---

## CSS Styling & Theme

### style.css (Main Stylesheet)

```css
/* ============================================
   USB Speed Test Application Stylesheet
   Premium Dark Theme with Glassmorphism
   ============================================ */

:root {
    /* Color Palette */
    --color-primary: #00d4ff;
    --color-primary-dark: #0099cc;
    --color-secondary: #ff006e;
    --color-accent: #8338ec;
    
    --color-bg-primary: #0f0f1e;
    --color-bg-secondary: #1a1a2e;
    --color-bg-tertiary: #16213e;
    
    --color-text-primary: #ffffff;
    --color-text-secondary: #b0b0b0;
    --color-text-tertiary: #808080;
    
    --color-success: #00ff88;
    --color-warning: #ffaa00;
    --color-error: #ff3333;
    --color-info: #00d4ff;
    
    --color-border: rgba(255, 255, 255, 0.1);
    --color-border-light: rgba(255, 255, 255, 0.05);
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    
    /* Typography */
    --font-primary: 'Outfit', sans-serif;
    --font-secondary: 'Inter', sans-serif;
    
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
    --font-size-2xl: 32px;
    --font-size-3xl: 48px;
    
    /* Border Radius */
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    
    /* Shadows */
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.5);
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
    
    /* Z-indexes */
    --z-base: 0;
    --z-dropdown: 10;
    --z-modal: 100;
    --z-toast: 1000;
}

/* ============================================
   Global Styles
   ============================================ */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    font-size: 16px;
}

body {
    font-family: var(--font-secondary);
    background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
    color: var(--color-text-primary);
    background-attachment: fixed;
    overflow-x: hidden;
}

/* ============================================
   App Container
   ============================================ */

.app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: var(--color-bg-primary);
}

/* ============================================
   Header
   ============================================ */

.app-header {
    background: rgba(26, 26, 46, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--color-border);
    padding: var(--spacing-lg) var(--spacing-xl);
    position: sticky;
    top: 0;
    z-index: 50;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
}

.header-left {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.app-title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    font-family: var(--font-primary);
    background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin: 0;
}

.app-subtitle {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0;
}

.header-right {
    display: flex;
    gap: var(--spacing-md);
}

.header-actions {
    display: flex;
    gap: var(--spacing-sm);
}

/* ============================================
   Button Styles
   ============================================ */

.btn {
    font-family: var(--font-primary);
    font-size: var(--font-size-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-normal);
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    user-select: none;
}

.btn-primary {
    background: var(--color-primary);
    color: var(--color-bg-primary);
}

.btn-primary:hover {
    background: var(--color-primary-dark);
    box-shadow: 0 0 24px rgba(0, 212, 255, 0.3);
    transform: translateY(-2px);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: var(--color-primary);
}

.btn-danger {
    background: var(--color-error);
    color: white;
}

.btn-danger:hover {
    background: #ff5555;
    box-shadow: 0 0 24px rgba(255, 51, 51, 0.3);
}

.btn-icon {
    width: 40px;
    height: 40px;
    padding: 0;
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
}

.btn-icon:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* ============================================
   Tab Navigation
   ============================================ */

.tab-navigation {
    display: flex;
    gap: var(--spacing-sm);
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
    overflow-x: auto;
    background: rgba(26, 26, 46, 0.5);
}

.tab-button {
    padding: var(--spacing-sm) var(--spacing-md);
    background: transparent;
    border: none;
    color: var(--color-text-secondary);
    font-family: var(--font-primary);
    font-weight: 600;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all var(--transition-normal);
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.tab-button:hover {
    color: var(--color-text-primary);
    border-bottom-color: var(--color-primary);
}

.tab-button.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
}

/* ============================================
   Tab Contents
   ============================================ */

.tab-contents {
    flex: 1;
    overflow-y: auto;
}

.tab-content {
    display: none;
    padding: var(--spacing-xl);
    animation: fadeIn var(--transition-normal);
}

.tab-content.active {
    display: block;
}

.tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-xl);
    flex-wrap: wrap;
    gap: var(--spacing-lg);
}

.tab-header h2 {
    font-size: var(--font-size-xl);
    font-weight: 700;
    margin: 0;
}

/* ============================================
   Device Grid & Cards
   ============================================ */

.devices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.device-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: all var(--transition-normal);
    cursor: pointer;
}

.device-card:hover {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.05) 100%);
    border-color: var(--color-primary);
    box-shadow: 0 0 24px rgba(0, 212, 255, 0.2);
    transform: translateY(-4px);
}

.device-icon {
    font-size: var(--font-size-3xl);
    margin-bottom: var(--spacing-md);
    color: var(--color-primary);
}

.device-name {
    font-size: var(--font-size-lg);
    font-weight: 700;
    margin-bottom: var(--spacing-sm);
    font-family: var(--font-primary);
}

.device-info {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    line-height: 1.6;
}

.device-info-item {
    display: flex;
    justify-content: space-between;
    margin: var(--spacing-xs) 0;
}

.device-actions {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-lg);
}

.device-actions .btn {
    flex: 1;
}

/* ============================================
   Progress Bar
   ============================================ */

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-md);
    overflow: hidden;
    margin: var(--spacing-md) 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
    width: 0%;
    transition: width var(--transition-normal);
    box-shadow: 0 0 16px rgba(0, 212, 255, 0.5);
}

/* ============================================
   Modal
   ============================================ */

.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    z-index: var(--z-modal);
    align-items: center;
    justify-content: center;
    animation: fadeIn var(--transition-normal);
}

.modal.active {
    display: flex;
}

.modal-content {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 0 48px rgba(0, 0, 0, 0.8);
    animation: slideUp var(--transition-normal);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.modal-close {
    background: none;
    border: none;
    color: var(--color-text-primary);
    cursor: pointer;
    font-size: var(--font-size-lg);
    transition: color var(--transition-normal);
}

.modal-close:hover {
    color: var(--color-primary);
}

/* ============================================
   Toast Notifications
   ============================================ */

.toast-container {
    position: fixed;
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    z-index: var(--z-toast);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    pointer-events: none;
}

.toast {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md) var(--spacing-lg);
    color: var(--color-text-primary);
    box-shadow: 0 0 24px rgba(0, 0, 0, 0.4);
    pointer-events: auto;
    animation: slideInRight var(--transition-normal);
    min-width: 300px;
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.toast.success {
    border-color: var(--color-success);
}

.toast.error {
    border-color: var(--color-error);
}

.toast.warning {
    border-color: var(--color-warning);
}

.toast.info {
    border-color: var(--color-info);
}

/* ============================================
   Footer
   ============================================ */

.app-footer {
    background: rgba(26, 26, 46, 0.8);
    border-top: 1px solid var(--color-border);
    padding: var(--spacing-lg);
    text-align: center;
}

.footer-content {
    display: flex;
    justify-content: center;
    gap: var(--spacing-xl);
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

.footer-text {
    margin: 0;
}

/* ============================================
   Animations
   ============================================ */

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes slideInRight {
    from {
        transform: translateX(100px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

/* Loading spinner */
.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
```

---

## JavaScript Implementation

### app.js (Main Application Controller)

```javascript
/**
 * USB Speed Test Application
 * Main application controller and API bridge
 */

class USBSpeedTestApp {
    constructor() {
        this.api = window.pywebview?.api;
        this.config = {};
        this.testHistory = [];
        this.currentTest = null;
        this.initialized = false;
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Wait for PyWebView to be ready
            await this.waitForAPI();
            
            // Load configuration
            await this.loadConfig();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadDevices();
            
            this.initialized = true;
            this.showToast('Application loaded successfully', 'success');
        } catch (error) {
            console.error('Initialization error:', error);
            this.showToast('Failed to initialize application', 'error');
        }
    }

    /**
     * Wait for PyWebView API to be available
     */
    async waitForAPI() {
        return new Promise((resolve) => {
            const checkAPI = () => {
                if (window.pywebview?.api) {
                    this.api = window.pywebview.api;
                    resolve();
                } else {
                    setTimeout(checkAPI, 100);
                }
            };
            checkAPI();
        });
    }

    /**
     * Load application configuration
     */
    async loadConfig() {
        try {
            const response = await this.api.get_config();
            if (response.success) {
                this.config = response.data;
            }
        } catch (error) {
            console.warn('Failed to load configuration:', error);
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab-button')));
        });

        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.loadDevices());

        // Settings button
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.openSettings());

        // Device type filter
        document.getElementById('deviceTypeFilter')?.addEventListener('change', (e) => {
            this.filterDevicesByType(e.target.value);
        });

        // Auto-refresh devices every 5 seconds
        setInterval(() => this.loadDevices(), 5000);
    }

    /**
     * Switch between tabs
     */
    switchTab(tabButton) {
        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });

        // Remove active class from all contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Add active class to clicked button
        tabButton.classList.add('active');

        // Get tab name and show corresponding content
        const tabName = tabButton.dataset.tab;
        const tabContent = document.getElementById(`${tabName}-tab`);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    }

    /**
     * Load all connected devices
     */
    async loadDevices() {
        try {
            const response = await this.api.get_all_devices();
            
            if (response.success) {
                this.displayDevices(response.data.devices);
                this.updateStatusText(`${response.data.devices.length} devices detected`);
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            this.showToast('Failed to load devices', 'error');
        }
    }

    /**
     * Display devices in the grid
     */
    displayDevices(devices) {
        const grid = document.getElementById('devices-list');
        if (!grid) return;

        grid.innerHTML = '';

        if (devices.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--color-text-secondary);">No USB devices detected</p>';
            return;
        }

        devices.forEach(device => {
            const card = this.createDeviceCard(device);
            grid.appendChild(card);
        });
    }

    /**
     * Create a device card element
     */
    createDeviceCard(device) {
        const card = document.createElement('div');
        card.className = 'device-card';
        card.innerHTML = `
            <div class="device-icon">${this.getDeviceIcon(device.device_type)}</div>
            <h3 class="device-name">${device.name}</h3>
            <div class="device-info">
                <div class="device-info-item">
                    <span>Type:</span>
                    <strong>${device.device_type}</strong>
                </div>
                <div class="device-info-item">
                    <span>Vendor:</span>
                    <strong>${device.vendor}</strong>
                </div>
                ${device.mount_point ? `
                <div class="device-info-item">
                    <span>Mount:</span>
                    <strong>${device.mount_point}</strong>
                </div>
                ` : ''}
                ${device.file_system ? `
                <div class="device-info-item">
                    <span>File System:</span>
                    <strong>${device.file_system}</strong>
                </div>
                ` : ''}
            </div>
            <div class="device-actions">
                ${device.device_type === 'STORAGE' ? `
                    <button class="btn btn-primary" onclick="app.runSpeedTest('${device.id}')">
                        <i class="fas fa-tachometer-alt"></i> Speed Test
                    </button>
                ` : ''}
                <button class="btn btn-secondary" onclick="app.showDeviceDetails('${device.id}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
            </div>
        `;
        return card;
    }

    /**
     * Get icon for device type
     */
    getDeviceIcon(deviceType) {
        const icons = {
            'STORAGE': '<i class="fas fa-hdd"></i>',
            'AUDIO': '<i class="fas fa-headphones"></i>',
            'CAMERA': '<i class="fas fa-camera"></i>',
            'PRINTER': '<i class="fas fa-print"></i>',
            'INPUT': '<i class="fas fa-keyboard"></i>',
            'MOBILE': '<i class="fas fa-mobile-alt"></i>',
            'GENERIC': '<i class="fas fa-usb"></i>',
        };
        return icons[deviceType] || icons['GENERIC'];
    }

    /**
     * Run speed test on a device
     */
    async runSpeedTest(deviceId) {
        try {
            // Show progress modal
            const modal = document.getElementById('progressModal');
            modal.classList.add('active');

            const result = await this.api.run_speed_test(deviceId, 100);

            if (result.success) {
                this.currentTest = result.data;
                this.testHistory.push(result.data);
                
                modal.classList.remove('active');
                this.showToast('Speed test completed successfully', 'success');
                
                // Show results
                this.showSpeedTestResults(result.data);
            }
        } catch (error) {
            console.error('Speed test error:', error);
            document.getElementById('progressModal').classList.remove('active');
            this.showToast('Speed test failed', 'error');
        }
    }

    /**
     * Show speed test results
     */
    showSpeedTestResults(testResult) {
        const panel = document.getElementById('speedtest-panel');
        if (!panel) return;

        panel.innerHTML = `
            <div class="test-result-card">
                <h3>${testResult.device_name}</h3>
                <div class="result-metrics">
                    <div class="metric">
                        <label>Write Speed</label>
                        <value>${testResult.write_speed_mbps.toFixed(2)} MB/s</value>
                    </div>
                    <div class="metric">
                        <label>Read Speed</label>
                        <value>${testResult.read_speed_mbps.toFixed(2)} MB/s</value>
                    </div>
                    <div class="metric">
                        <label>Test Size</label>
                        <value>${testResult.test_size_mb} MB</value>
                    </div>
                    <div class="metric">
                        <label>Duration</label>
                        <value>${testResult.test_duration_sec.toFixed(2)}s</value>
                    </div>
                </div>
                <div class="test-actions">
                    <button class="btn btn-primary" onclick="app.generateReport('${testResult.test_id}')">
                        <i class="fas fa-file-pdf"></i> Generate Report
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Generate report from test result
     */
    async generateReport(testId) {
        try {
            const response = await this.api.generate_device_report(testId);
            
            if (response.success) {
                this.showToast('Report generated successfully', 'success');
                // Open report in browser
                await this.api.open_report(response.data.report_path);
            }
        } catch (error) {
            console.error('Report generation error:', error);
            this.showToast('Failed to generate report', 'error');
        }
    }

    /**
     * Filter devices by type
     */
    filterDevicesByType(deviceType) {
        if (!deviceType) {
            this.loadDevices();
            return;
        }

        const cards = document.querySelectorAll('.device-card');
        cards.forEach(card => {
            const typeText = card.querySelector('.device-info-item:nth-child(2)')?.innerText;
            card.style.display = typeText && typeText.includes(deviceType) ? '' : 'none';
        });
    }

    /**
     * Show device details modal
     */
    async showDeviceDetails(deviceId) {
        // Implementation for showing detailed device information
    }

    /**
     * Open settings modal
     */
    openSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.add('active');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    /**
     * Get icon for toast type
     */
    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Update status text
     */
    updateStatusText(text) {
        const statusElement = document.getElementById('statusText');
        if (statusElement) {
            statusElement.textContent = text;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new USBSpeedTestApp();
});
```

---

## Component Examples

### Device List Component (device-list.js)

```javascript
class DeviceListComponent {
    constructor(app) {
        this.app = app;
        this.devices = [];
    }

    async loadDevices() {
        const response = await this.app.api.get_all_devices();
        if (response.success) {
            this.devices = response.data.devices;
            this.render();
        }
    }

    render() {
        const container = document.getElementById('devices-list');
        container.innerHTML = '';
        
        this.devices.forEach(device => {
            const element = this.createDeviceElement(device);
            container.appendChild(element);
        });
    }

    createDeviceElement(device) {
        const element = document.createElement('div');
        element.className = 'device-card';
        element.innerHTML = `
            <!-- Device card HTML -->
        `;
        return element;
    }
}
```

---

## Error Handling

### API Error Response Handling

```javascript
async handleAPIResponse(response) {
    if (!response.success) {
        const errorMessage = response.error || 'Unknown error occurred';
        console.error('API Error:', errorMessage);
        this.showToast(errorMessage, 'error');
        return null;
    }
    return response.data;
}
```

### User Feedback Pattern

```javascript
// Always provide feedback for long-running operations
async runLongOperation() {
    try {
        this.showToast('Operation starting...', 'info');
        const result = await this.api.longOperation();
        
        if (result.success) {
            this.showToast('Operation completed', 'success');
        } else {
            this.showToast(result.error, 'error');
        }
    } catch (error) {
        this.showToast('Operation failed', 'error');
    }
}
```

---

## Performance Optimization

### 1. Lazy Loading

```javascript
// Load components only when tab becomes active
const tabButtons = document.querySelectorAll('.tab-button');
tabButtons.forEach(button => {
    button.addEventListener('click', async (e) => {
        const tabName = e.target.dataset.tab;
        
        if (tabName === 'comparison' && !this.comparisonLoaded) {
            await this.loadComparisonPanel();
            this.comparisonLoaded = true;
        }
    });
});
```

### 2. Debouncing Device Enumeration

```javascript
const debouncedRefresh = this.debounce(() => {
    this.loadDevices();
}, 1000);

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
```

### 3. Caching Device Lists

```javascript
class DeviceCache {
    constructor(ttl = 5000) {
        this.cache = null;
        this.ttl = ttl;
        this.lastUpdate = 0;
    }

    async getDevices(api) {
        const now = Date.now();
        
        if (this.cache && (now - this.lastUpdate) < this.ttl) {
            return this.cache;
        }
        
        const response = await api.get_all_devices();
        if (response.success) {
            this.cache = response.data.devices;
            this.lastUpdate = now;
        }
        
        return this.cache;
    }
}
```

---

**End of API & Frontend Implementation Guide**
