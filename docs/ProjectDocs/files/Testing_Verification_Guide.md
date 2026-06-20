# Testing & Verification Guide
## USB Speed Test and Monitoring Application

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Platform Testing](#platform-testing)
5. [Performance Testing](#performance-testing)
6. [User Acceptance Testing](#user-acceptance-testing)
7. [Quality Metrics](#quality-metrics)
8. [Bug Reporting & Triage](#bug-reporting--triage)

---

## Testing Strategy

### Test Pyramid

```
        ▲
       /|\
      / | \
     /  |  \  End-to-End Tests
    /   |   \
   /____|____\
   /    |    \
  /     |     \ Integration Tests
 /      |      \
/_______|_______\
/        |        \
/         |         \ Unit Tests
/__________|_________\
```

### Test Coverage Goals

```
Target Coverage:
  ├── Unit Tests: 80%+ coverage of modules
  ├── Integration Tests: 70%+ coverage of APIs
  ├── Platform Tests: 100% on Windows, macOS, Linux
  ├── Performance Tests: 10% degradation threshold
  └── Acceptance Tests: 100% of user stories
```

### Test Execution Timeline

```
Development Phase:
  └─ Unit Tests (continuous, on every commit)

Integration Phase:
  ├─ Integration Tests (daily)
  └─ Smoke Tests (per feature)

Release Phase:
  ├─ Full Regression Testing
  ├─ Platform Testing (all OS versions)
  ├─ Performance Testing
  ├─ Security Testing
  └─ UAT

Production:
  └─ Monitoring & Issue Tracking
```

---

## Unit Testing

### Test Structure

```
tests/
├── unit/
│   ├── __init__.py
│   ├── test_usb_detector.py
│   ├── test_speed_test.py
│   ├── test_report_generator.py
│   ├── test_monitor_service.py
│   └── test_platform_utils.py
├── integration/
│   └── test_api.py
├── fixtures/
│   ├── conftest.py
│   └── mock_data.py
└── performance/
    └── test_benchmarks.py
```

### conftest.py - Pytest Fixtures

```python
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_config():
    """Mock application configuration"""
    return {
        'speed_test': {
            'default_test_size_mb': 10,
            'chunk_size_mb': 1,
            'timeout_seconds': 60,
        },
        'monitoring': {
            'enabled': True,
            'check_interval_seconds': 5,
            'low_disk_threshold_percent': 10,
        },
    }

@pytest.fixture
def mock_device():
    """Mock USB device"""
    return {
        'id': 'usb-test-001',
        'name': 'Test USB Drive',
        'vendor': 'TestVendor',
        'vendor_id': '0001',
        'product_id': '0001',
        'serial': 'TEST123',
        'device_type': 'STORAGE',
        'bus_type': 'USB',
        'is_removable': True,
        'mount_point': '/media/test',
        'device_path': '/dev/sda1',
        'file_system': 'FAT32',
    }

@pytest.fixture
def mock_speed_test_result():
    """Mock speed test result"""
    return {
        'test_id': 'test-001',
        'device_id': 'usb-001',
        'device_name': 'Test Drive',
        'write_speed_mbps': 50.0,
        'read_speed_mbps': 100.0,
        'test_size_mb': 100,
        'timestamp': '2024-06-20T14:30:00Z',
    }

@pytest.fixture
def api_client(mock_config, mock_device):
    """Mock API client"""
    api = Mock()
    api.get_config.return_value = {'success': True, 'data': mock_config}
    api.get_all_devices.return_value = {'success': True, 'data': {'devices': [mock_device]}}
    return api
```

### Test Examples

#### test_usb_detector.py

```python
import pytest
from modules.usb_detector import DeviceDetector, DeviceType

class TestDeviceDetector:
    """Test USB device detection"""
    
    def test_detector_initialization(self):
        """Test detector can be initialized"""
        detector = DeviceDetector()
        assert detector is not None
    
    def test_get_all_devices_returns_list(self, mock_device):
        """Test get_all_devices returns a list"""
        detector = DeviceDetector()
        
        # Mock the platform-specific method
        with patch.object(detector, '_detect_devices', return_value=[mock_device]):
            devices = detector.get_all_devices()
            
            assert isinstance(devices, list)
            assert len(devices) > 0
    
    def test_device_has_required_fields(self, mock_device):
        """Test device object has all required fields"""
        required_fields = [
            'id', 'name', 'vendor', 'device_type', 'bus_type',
            'is_removable', 'device_path'
        ]
        
        for field in required_fields:
            assert field in mock_device, f"Missing field: {field}"
    
    def test_classify_device_by_type(self, detector):
        """Test device type classification"""
        device_data = {
            'name': 'Kingston DataTraveler Storage',
            'class': 0x08,  # Storage class
        }
        
        device_type = detector.classify_device(device_data)
        assert device_type == DeviceType.STORAGE
    
    def test_filter_devices_by_type(self, detector, mock_device):
        """Test filtering devices by type"""
        devices = [
            {**mock_device, 'device_type': 'STORAGE'},
            {**mock_device, 'id': 'audio-001', 'device_type': 'AUDIO'},
            {**mock_device, 'id': 'camera-001', 'device_type': 'CAMERA'},
        ]
        
        storage_devices = detector.filter_by_type(devices, 'STORAGE')
        assert len(storage_devices) == 1
        assert storage_devices[0]['device_type'] == 'STORAGE'
    
    @pytest.mark.parametrize('device_type,icon', [
        ('STORAGE', 'hdd'),
        ('AUDIO', 'headphones'),
        ('CAMERA', 'camera'),
    ])
    def test_device_type_to_icon_mapping(self, detector, device_type, icon):
        """Test device type to icon mapping"""
        icon_result = detector.get_icon_for_type(device_type)
        assert icon in icon_result
```

#### test_speed_test.py

```python
import pytest
import tempfile
from pathlib import Path
from modules.speed_test import SpeedTester

class TestSpeedTester:
    """Test speed testing functionality"""
    
    def test_tester_initialization(self):
        """Test speed tester initialization"""
        tester = SpeedTester()
        assert tester is not None
    
    def test_write_test_creates_file(self, temp_dir):
        """Test write test creates temporary file"""
        tester = SpeedTester()
        
        bytes_written, duration = tester.write_test(str(temp_dir), size_mb=1)
        
        assert bytes_written > 0
        assert duration > 0
        assert bytes_written == 1024 * 1024  # 1 MB
    
    def test_read_test_measures_speed(self, temp_dir):
        """Test read test measures file read speed"""
        tester = SpeedTester()
        
        # Create test file first
        test_file = temp_dir / 'test_file.bin'
        test_file.write_bytes(b'0' * (1024 * 1024))  # 1 MB
        
        bytes_read, duration = tester.read_test(str(test_file))
        
        assert bytes_read > 0
        assert duration > 0
    
    def test_calculate_speed_mbps(self, tester):
        """Test speed calculation"""
        # 100 MB in 2 seconds = 50 MB/s
        bytes_transferred = 100 * 1024 * 1024
        duration = 2.0
        
        speed = tester.calculate_speed(bytes_transferred, duration)
        
        assert abs(speed - 50.0) < 0.1  # Allow small floating point error
    
    def test_cleanup_removes_test_file(self, temp_dir):
        """Test cleanup removes temporary files"""
        tester = SpeedTester()
        test_file = temp_dir / '__test_file__.dat'
        test_file.write_bytes(b'test')
        
        assert test_file.exists()
        
        tester.cleanup(str(temp_dir))
        
        assert not test_file.exists()
    
    def test_speed_test_timeout(self, temp_dir):
        """Test speed test respects timeout"""
        tester = SpeedTester(timeout=1)
        
        with pytest.raises(TimeoutError):
            # Try to write a large file with short timeout
            tester.write_test(str(temp_dir), size_mb=1000)
```

#### test_report_generator.py

```python
import pytest
from modules.report_generator import ReportGenerator

class TestReportGenerator:
    """Test HTML report generation"""
    
    def test_report_generation(self, mock_speed_test_result, temp_dir):
        """Test basic report generation"""
        generator = ReportGenerator()
        
        html_content = generator.generate_device_report(
            mock_speed_test_result,
            output_dir=temp_dir
        )
        
        assert '<html' in html_content.lower()
        assert mock_speed_test_result['device_name'] in html_content
        assert 'MB/s' in html_content
    
    def test_report_contains_test_metrics(self, mock_speed_test_result, generator):
        """Test report contains all speed test metrics"""
        html = generator.generate_device_report(mock_speed_test_result)
        
        assert f"{mock_speed_test_result['write_speed_mbps']:.2f}" in html
        assert f"{mock_speed_test_result['read_speed_mbps']:.2f}" in html
        assert f"{mock_speed_test_result['test_size_mb']}" in html
    
    def test_comparison_report_generation(self, mock_speed_test_result, generator):
        """Test comparison report with multiple tests"""
        test_results = [
            {**mock_speed_test_result, 'test_id': 'test-001', 'device_name': 'Drive A'},
            {**mock_speed_test_result, 'test_id': 'test-002', 'device_name': 'Drive B'},
        ]
        
        html = generator.generate_comparison_report(test_results)
        
        assert 'Drive A' in html
        assert 'Drive B' in html
        assert '<table' in html.lower()  # Should contain comparison table
    
    def test_report_is_valid_html(self, mock_speed_test_result, generator):
        """Test generated report is valid HTML"""
        from html.parser import HTMLParser
        
        html = generator.generate_device_report(mock_speed_test_result)
        parser = HTMLParser()
        
        try:
            parser.feed(html)
            assert True  # If no exception, HTML is valid
        except Exception:
            pytest.fail("Generated HTML is invalid")
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_usb_detector.py -v

# Run with coverage report
pytest tests/unit/ --cov=src/modules --cov-report=html

# Run tests with markers
pytest -m "not slow" -v

# Run tests in parallel (faster execution)
pytest tests/unit/ -n auto
```

---

## Integration Testing

### test_api.py

```python
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from main import create_app

class TestAPIIntegration:
    """Test API integration"""
    
    @pytest.fixture
    async def app(self):
        """Create test application"""
        app = await create_app()
        yield app
        await app.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_devices_endpoint(self, app):
        """Test devices endpoint integration"""
        result = await app.api.get_all_devices()
        
        assert result['success'] is not None
        if result['success']:
            assert 'devices' in result['data']
            assert isinstance(result['data']['devices'], list)
    
    @pytest.mark.asyncio
    async def test_speed_test_endpoint(self, app):
        """Test speed test endpoint"""
        with patch('modules.speed_test.SpeedTester.run_speed_test') as mock_test:
            mock_test.return_value = {
                'test_id': 'test-001',
                'write_speed_mbps': 50.0,
                'read_speed_mbps': 100.0,
            }
            
            result = await app.api.run_speed_test('usb-001', 10)
            
            assert result['success'] is True
            assert 'write_speed_mbps' in result['data']
    
    @pytest.mark.asyncio
    async def test_report_generation_endpoint(self, app, mock_speed_test_result):
        """Test report generation endpoint"""
        with patch('modules.report_generator.ReportGenerator.generate_device_report') as mock_gen:
            mock_gen.return_value = '<html></html>'
            
            result = await app.api.generate_device_report('test-001')
            
            assert result['success'] is True
            assert 'report_path' in result['data']
```

---

## Platform Testing

### Platform Test Checklist

#### Windows 10/11 Testing

```
Device Detection:
  ☐ List USB storage devices (WMI method)
  ☐ List USB peripherals (audio, camera, input)
  ☐ Detect drive letters (C:, D:, E:, etc.)
  ☐ Handle multiple USB devices
  ☐ Handle removed devices gracefully

Speed Testing:
  ☐ Write test creates temp file
  ☐ Read test measures correct speed
  ☐ Cleanup removes temp files
  ☐ Handle write-protected drives
  ☐ Handle disconnection during test

UI/UX:
  ☐ Application starts without errors
  ☐ All tabs are functional
  ☐ Filter by device type works
  ☐ Refresh button updates device list
  ☐ Notifications display correctly

Installer:
  ☐ .exe installer creates files
  ☐ Start menu shortcuts created
  ☐ Uninstaller removes files
  ☐ Registry entries created
  ☐ Application can be upgraded
```

#### macOS (Intel & Apple Silicon) Testing

```
Device Detection:
  ☐ diskutil lists mounted volumes
  ☐ system_profiler detects USB devices
  ☐ Mounted point paths correct (/Volumes/...)
  ☐ Handle M1/M2 architecture
  ☐ Accessibility permissions dialog shown

Speed Testing:
  ☐ Write test on USB drive
  ☐ Read test measures correctly
  ☐ APFS, FAT32, exFAT file systems supported
  ☐ Eject handling during test

Notifications:
  ☐ System notifications display
  ☐ Menu bar icon appears
  ☐ Low disk notifications trigger

DMG Installation:
  ☐ DMG mounts correctly
  ☐ Drag-and-drop installation works
  ☐ Application runs from /Applications
  ☐ Gatekeeper accepts app
  ☐ Notarization verified
```

#### Linux Testing

```
Device Detection:
  ☐ lsblk detects USB drives
  ☐ /sys/class/block enumeration
  ☐ Mount points correctly identified
  ☐ Removable device detection
  ☐ Support Ubuntu, Debian, CentOS

Speed Testing:
  ☐ ext4, FAT32, NTFS file systems
  ☐ /dev/sdX device paths
  ☐ Direct device access
  ☐ Unmount/mount handling

Desktop Integration:
  ☐ Desktop entry file works
  ☐ notify-send notifications
  ☐ App menu integration
  ☐ AppImage execution permissions

AppImage:
  ☐ Bundle integrates dependencies
  ☐ FUSE2 or FUSE3 support
  ☐ Runs on different distros
  ☐ No root required
```

### Platform Test Automation

```python
import sys
import pytest

@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only test")
def test_windows_wmi_detection():
    """Test WMI device detection on Windows"""
    from modules.usb_detector import WindowsDeviceDetector
    detector = WindowsDeviceDetector()
    devices = detector.get_all_usb_devices()
    assert isinstance(devices, list)

@pytest.mark.skipif(sys.platform != 'darwin', reason="macOS-only test")
def test_macos_diskutil_detection():
    """Test diskutil device detection on macOS"""
    from modules.usb_detector import MacOSDeviceDetector
    detector = MacOSDeviceDetector()
    devices = detector.get_all_usb_devices()
    assert isinstance(devices, list)

@pytest.mark.skipif(not sys.platform.startswith('linux'), reason="Linux-only test")
def test_linux_lsblk_detection():
    """Test lsblk device detection on Linux"""
    from modules.usb_detector import LinuxDeviceDetector
    detector = LinuxDeviceDetector()
    devices = detector.get_all_usb_devices()
    assert isinstance(devices, list)
```

---

## Performance Testing

### Benchmark Tests

```python
import pytest
import time

class TestPerformance:
    """Performance benchmarks"""
    
    def test_device_enumeration_speed(self, benchmark):
        """Benchmark device enumeration"""
        from modules.usb_detector import DeviceDetector
        
        def enumerate_devices():
            detector = DeviceDetector()
            return detector.get_all_devices()
        
        result = benchmark(enumerate_devices)
        assert result is not None
    
    def test_speed_test_performance(self, benchmark, temp_dir):
        """Benchmark speed test on small file"""
        from modules.speed_test import SpeedTester
        
        def run_test():
            tester = SpeedTester()
            return tester.write_test(str(temp_dir), size_mb=10)
        
        result = benchmark(run_test)
        bytes_written, duration = result
        
        # Should complete in reasonable time (< 5 seconds for 10 MB)
        assert duration < 5.0
    
    def test_report_generation_speed(self, benchmark, mock_speed_test_result):
        """Benchmark report generation"""
        from modules.report_generator import ReportGenerator
        
        def generate_report():
            generator = ReportGenerator()
            return generator.generate_device_report(mock_speed_test_result)
        
        result = benchmark(generate_report)
        assert len(result) > 100  # Should generate meaningful HTML
    
    def test_ui_responsiveness(self, benchmark):
        """Benchmark UI update speed"""
        def update_ui():
            # Simulate UI update
            time.sleep(0.01)  # Placeholder
        
        result = benchmark(update_ui)
        # Should stay responsive (< 100ms)
        assert result is None
```

### Load Testing

```bash
# Run under load with stress testing
pytest tests/performance/ --stress --workers 4

# Memory profiling
python -m memory_profiler main.py

# CPU profiling
python -m cProfile -o profile.stats main.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

---

## User Acceptance Testing

### UAT Test Scenarios

#### Scenario 1: Detect and Benchmark USB Drive

```
Steps:
  1. Start application
  2. Connect USB drive
  3. Observe device listed in "Devices" tab
  4. Click "Speed Test" button on USB device
  5. Wait for test to complete
  6. Verify results displayed with MB/s values
  7. Click "Generate Report" button
  8. Verify report opens in browser

Expected Results:
  ✓ Device detected within 2 seconds
  ✓ Speed test completes in < 30 seconds
  ✓ Results show realistic speeds (0-500 MB/s)
  ✓ Report contains device info and speed data
  ✓ Report renders correctly in browser
```

#### Scenario 2: Compare Multiple Devices

```
Steps:
  1. Connect 2-3 USB drives
  2. Run speed test on each device
  3. Switch to "Comparison" tab
  4. Verify all test results displayed side-by-side
  5. Click "Generate Comparison Report"
  6. Verify report shows rankings

Expected Results:
  ✓ All tests recorded in session
  ✓ Comparison table shows all devices
  ✓ Rankings correctly calculated
  ✓ Comparison report is printable
```

#### Scenario 3: Device Filter and Sort

```
Steps:
  1. Start application with multiple USB devices
  2. Filter by "AUDIO" device type
  3. Verify only audio devices shown
  4. Filter by "STORAGE" device type
  5. Verify only storage devices shown

Expected Results:
  ✓ Filter responds immediately
  ✓ Correct devices displayed
  ✓ Device count updates
```

---

## Quality Metrics

### Code Coverage Report

```
Module Coverage Report:
├── modules/usb_detector.py          92%
├── modules/speed_test.py            88%
├── modules/report_generator.py      95%
├── modules/monitor_service.py       75%
├── modules/platform_utils.py        85%
├── utils/logger.py                  90%
└── TOTAL                            89%
```

### Test Execution Results

```
Test Results Summary:
├── Unit Tests:           145 passed, 2 skipped, 0 failed
├── Integration Tests:    28 passed, 0 skipped, 0 failed
├── Platform Tests:
│   ├── Windows:          42 passed
│   ├── macOS:            42 passed
│   └── Linux:            42 passed
├── Performance Tests:    8 passed, 0 failed
└── UAT Tests:            12 passed, 0 failed

Total: 319 tests passed

Coverage: 89%
Build Time: 45 minutes
Test Time: 12 minutes
```

### Defect Metrics

```
Defect Severity Distribution:
├── Critical (blocks release):    0
├── High (major impact):          1
├── Medium (minor impact):        3
└── Low (cosmetic):              5

Total: 9 defects (all resolved)

Defect Density: 0.9 per 1000 LOC (target: <1.0)
```

---

## Bug Reporting & Triage

### Bug Report Template

```markdown
# Bug Report

## Title
[Brief description of the issue]

## Platform
- OS: [Windows 10/macOS 12/Ubuntu 22.04]
- Application Version: 1.0.0
- Build Number: 20240620

## Severity
[ ] Critical (blocks usage)
[ ] High (significant impact)
[ ] Medium (moderate impact)
[ ] Low (cosmetic)

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [etc.]

## Expected Result
[What should happen]

## Actual Result
[What actually happened]

## Screenshots/Videos
[Attach if relevant]

## Error Logs
```
[Paste relevant log entries]
```

## Additional Context
[Any other relevant information]
```

### Triage Process

```
Bug Reception:
  ├─ Verify reproducibility (Dev)
  ├─ Assign severity level
  ├─ Assign to developer
  └─ Add to sprint/milestone

Investigation:
  ├─ Reproduce locally
  ├─ Identify root cause
  ├─ Create minimal test case
  └─ Review similar issues

Resolution:
  ├─ Implement fix
  ├─ Write unit test for fix
  ├─ Test on all platforms
  └─ Code review

Verification:
  ├─ Re-run test case
  ├─ Run full test suite
  ├─ Run regression tests
  └─ Close issue

Post-Release:
  └─ Monitor for regressions
```

### Bug Tracking Workflow

```yaml
Bug States:
  Open:
    ├─ New: Created but not reviewed
    ├─ Triaged: Severity assigned
    └─ Assigned: Developer assigned
  
  In Progress:
    ├─ Investigation: Dev investigating
    ├─ In Development: Fix being implemented
    └─ In Testing: Fix being tested
  
  Review:
    ├─ Code Review: Awaiting review
    └─ QA Review: Awaiting QA approval
  
  Closed:
    ├─ Fixed: Bug resolved
    ├─ Cannot Reproduce: Could not verify
    ├─ Duplicate: Same as other issue
    └─ Not a Bug: Working as intended
```

---

## Continuous Testing

### Pre-Commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run quick unit tests before commit
pytest tests/unit/ -q --tb=short

if [ $? -ne 0 ]; then
    echo "Unit tests failed. Commit aborted."
    exit 1
fi

# Run code formatting check
black --check src/
flake8 src/ --max-line-length=100

echo "Pre-commit checks passed!"
```

### Daily Regression Testing

```bash
#!/bin/bash
# run_daily_tests.sh

echo "Starting daily regression tests..."

# Run all tests
pytest tests/ -v --tb=short --junit-xml=test-results.xml

# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# Run performance benchmarks
pytest tests/performance/ --benchmark-json=benchmark.json

# Email results
./scripts/send_test_report.sh
```

---

**End of Testing & Verification Guide**
