# Platform-Specific Implementation Guide
## USB Speed Test and Monitoring Application

**Target Platforms**: Windows 10+, macOS 10.13+, Linux (Ubuntu 18.04+, Debian 10+)

---

## Table of Contents

1. [Windows Implementation](#windows-implementation)
2. [macOS Implementation](#macos-implementation)
3. [Linux Implementation](#linux-implementation)
4. [Cross-Platform Abstraction Layer](#cross-platform-abstraction-layer)
5. [Testing on Each Platform](#testing-on-each-platform)

---

## Windows Implementation

### 1. USB Device Detection

#### Method 1: WMI (Recommended for comprehensive info)

```python
# modules/usb_detector.py - Windows implementation

import wmi
from typing import List, Dict
import subprocess
import json

class WindowsDeviceDetector:
    """Detect USB devices on Windows using WMI"""
    
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_all_usb_devices(self) -> List[Dict]:
        """Get all USB devices via WMI"""
        devices = []
        
        try:
            # Query USB devices through WMI
            for usb_device in self.wmi.Win32_USBHub():
                device_info = {
                    'name': usb_device.Description or 'Unknown Device',
                    'device_id': usb_device.DeviceID,
                    'vendor_id': self._extract_vid(usb_device.DeviceID),
                    'product_id': self._extract_pid(usb_device.DeviceID),
                    'pnp_device_id': usb_device.PNPDeviceID,
                    'device_type': self._classify_device(usb_device),
                    'bus_type': 'USB',
                }
                devices.append(device_info)
        
        except Exception as e:
            print(f"Error querying WMI: {e}")
        
        return devices
    
    def get_storage_devices(self) -> List[Dict]:
        """Get USB storage devices with mount points"""
        devices = []
        
        try:
            # Get logical disks
            for disk in self.wmi.Win32_LogicalDisk():
                if disk.DriveType == 2:  # Removable drive
                    device_info = {
                        'name': disk.VolumeName or disk.Name,
                        'mount_point': disk.Name,
                        'device_type': 'STORAGE',
                        'file_system': disk.FileSystem,
                        'serial': disk.VolumeSerialNumber,
                        'total_size': int(disk.Size) if disk.Size else 0,
                        'used_size': int(disk.Size) - int(disk.FreeSpace) if disk.Size else 0,
                        'free_size': int(disk.FreeSpace) if disk.FreeSpace else 0,
                        'is_mounted': True,
                    }
                    devices.append(device_info)
            
            # Also query physical disks for USB drives
            for disk in self.wmi.Win32_DiskDrive():
                if 'USB' in disk.Model.upper():
                    device_info = {
                        'name': disk.Model,
                        'device_path': disk.DeviceID,
                        'device_type': 'STORAGE',
                        'serial': disk.SerialNumber,
                        'size': int(disk.Size) if disk.Size else 0,
                        'interface_type': disk.InterfaceType,
                    }
                    devices.append(device_info)
        
        except Exception as e:
            print(f"Error querying storage devices: {e}")
        
        return devices
    
    def get_device_by_path(self, drive_letter: str) -> Dict:
        """Get detailed info for specific drive"""
        try:
            for disk in self.wmi.Win32_LogicalDisk():
                if disk.Name == drive_letter:
                    return {
                        'name': disk.VolumeName or disk.Name,
                        'mount_point': disk.Name,
                        'file_system': disk.FileSystem,
                        'total_bytes': int(disk.Size) if disk.Size else 0,
                        'free_bytes': int(disk.FreeSpace) if disk.FreeSpace else 0,
                        'used_bytes': int(disk.Size) - int(disk.FreeSpace) if disk.Size else 0,
                    }
        except Exception as e:
            print(f"Error getting device details: {e}")
        
        return None
    
    @staticmethod
    def _extract_vid(device_id: str) -> str:
        """Extract Vendor ID from device ID"""
        if 'VID_' in device_id:
            return device_id.split('VID_')[1][:4]
        return 'UNKNOWN'
    
    @staticmethod
    def _extract_pid(device_id: str) -> str:
        """Extract Product ID from device ID"""
        if 'PID_' in device_id:
            return device_id.split('PID_')[1][:4]
        return 'UNKNOWN'
    
    @staticmethod
    def _classify_device(usb_device) -> str:
        """Classify device type based on class code"""
        class_map = {
            '00': 'DEVICE',
            '01': 'AUDIO',
            '02': 'COMM',
            '03': 'INPUT',
            '05': 'PHYSICAL',
            '06': 'IMAGE',  # Camera
            '07': 'PRINTER',
            '08': 'STORAGE',
            '09': 'HUB',
            '0A': 'CDC_DATA',
            'FF': 'VENDOR',
        }
        
        try:
            # Parse class from PnP ID or use heuristic
            device_desc = usb_device.Description.upper()
            if 'STORAGE' in device_desc or 'DRIVE' in device_desc:
                return 'STORAGE'
            elif 'AUDIO' in device_desc or 'SPEAKER' in device_desc or 'HEADPHONE' in device_desc:
                return 'AUDIO'
            elif 'CAMERA' in device_desc or 'WEBCAM' in device_desc:
                return 'CAMERA'
            elif 'KEYBOARD' in device_desc or 'MOUSE' in device_desc:
                return 'INPUT'
            elif 'PRINTER' in device_desc:
                return 'PRINTER'
        except:
            pass
        
        return 'GENERIC'
```

#### Method 2: PowerShell (Alternative/Backup)

```python
def get_devices_via_powershell() -> List[Dict]:
    """Fallback method using PowerShell"""
    
    ps_script = """
    Get-WmiObject Win32_USBHub | Select-Object Description, DeviceID, 
        PNPDeviceID, Service | ConvertTo-Json
    """
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return data
    except Exception as e:
        print(f"PowerShell query failed: {e}")
    
    return []
```

### 2. File Operations for Speed Testing

```python
# modules/speed_test.py - Windows-specific file operations

import os
import tempfile
from pathlib import Path
import time

class WindowsSpeedTester:
    """Windows-specific speed test implementation"""
    
    def __init__(self):
        self.test_file_name = "__usb_speedtest_temp__.dat"
    
    def write_test(self, device_path: str, size_mb: int = 100) -> Tuple[float, float]:
        """
        Perform write speed test
        device_path: e.g., "D:" (Windows drive letter)
        
        Returns: (total_bytes_written, duration_seconds)
        """
        test_file_path = os.path.join(device_path + os.sep, self.test_file_name)
        chunk_size = 1024 * 1024  # 1 MB chunks
        total_size = size_mb * 1024 * 1024
        
        start_time = time.perf_counter()
        bytes_written = 0
        
        try:
            with open(test_file_path, 'wb', buffering=0) as f:  # Unbuffered
                while bytes_written < total_size:
                    chunk = os.urandom(chunk_size)
                    f.write(chunk)
                    bytes_written += len(chunk)
                
                # Force flush to disk
                os.fsync(f.fileno())
        
        except IOError as e:
            raise Exception(f"Write test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_written, duration
    
    def read_test(self, device_path: str, file_path: str) -> Tuple[float, float]:
        """
        Perform read speed test
        
        Returns: (total_bytes_read, duration_seconds)
        """
        chunk_size = 1024 * 1024  # 1 MB chunks
        start_time = time.perf_counter()
        bytes_read = 0
        
        try:
            with open(file_path, 'rb', buffering=0) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
        
        except IOError as e:
            raise Exception(f"Read test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_read, duration
    
    def cleanup(self, device_path: str):
        """Remove temporary test file"""
        test_file_path = os.path.join(device_path + os.sep, self.test_file_name)
        
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file: {e}")
```

### 3. Default Data Directory

```python
# config.py - Windows paths

import os
from pathlib import Path

WINDOWS_BASE_DIR = Path("C:\\ProgramData\\UBSSpeedTest")

WINDOWS_PATHS = {
    'data_dir': WINDOWS_BASE_DIR,
    'reports_dir': WINDOWS_BASE_DIR / "reports",
    'logs_dir': WINDOWS_BASE_DIR / "logs",
    'config_file': WINDOWS_BASE_DIR / "config.json",
    'cache_file': WINDOWS_BASE_DIR / "cache.json",
}

def ensure_windows_directories():
    """Create required Windows directories"""
    for directory in [
        WINDOWS_PATHS['data_dir'],
        WINDOWS_PATHS['reports_dir'],
        WINDOWS_PATHS['logs_dir'],
    ]:
        directory.mkdir(parents=True, exist_ok=True)
```

### 4. System Notifications (Windows)

```python
# modules/monitor_service.py - Windows notifications

from win10toast import ToastNotifier

class WindowsNotificationManager:
    """Windows 10+ notification system"""
    
    def __init__(self):
        self.toaster = ToastNotifier()
    
    def show_notification(self, title: str, message: str, duration: int = 5):
        """Show system notification (toast)"""
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")
```

### 5. Tray Icon (Windows)

```python
# Using pystray library

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

class WindowsTrayIcon:
    """Windows system tray integration"""
    
    def __init__(self, app_name: str, on_click_callback):
        self.app_name = app_name
        self.icon = None
        self.on_click_callback = on_click_callback
    
    def create_icon_image(self) -> Image.Image:
        """Create a simple tray icon"""
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple USB icon representation
        draw.rectangle([16, 16, 48, 48], outline='white', width=2)
        
        return image
    
    def start(self):
        """Start tray icon"""
        icon_image = self.create_icon_image()
        
        menu = Menu(
            MenuItem('Show', self.on_click_callback),
            MenuItem('Exit', lambda: self._quit_app())
        )
        
        self.icon = Icon(
            name=self.app_name,
            icon=icon_image,
            menu=menu
        )
        
        self.icon.run()
    
    def stop(self):
        """Stop tray icon"""
        if self.icon:
            self.icon.stop()
    
    def _quit_app(self):
        self.stop()
```

---

## macOS Implementation

### 1. USB Device Detection

```python
# modules/usb_detector.py - macOS implementation

import subprocess
import json
import plistlib
from typing import List, Dict

class MacOSDeviceDetector:
    """Detect USB devices on macOS"""
    
    def get_all_usb_devices(self) -> List[Dict]:
        """Get all USB devices using system_profiler"""
        devices = []
        
        try:
            # Use system_profiler to get USB data in JSON format
            result = subprocess.run(
                ['system_profiler', 'SPUSBDataType', '-json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                devices = self._parse_usb_data(data)
        
        except Exception as e:
            print(f"Error querying USB devices: {e}")
        
        return devices
    
    def _parse_usb_data(self, data: Dict) -> List[Dict]:
        """Parse USB data from system_profiler output"""
        devices = []
        
        try:
            usb_info = data.get('SPUSBDataType', [])
            
            for controller in usb_info:
                self._extract_devices_from_controller(
                    controller, 
                    devices
                )
        
        except Exception as e:
            print(f"Error parsing USB data: {e}")
        
        return devices
    
    def _extract_devices_from_controller(self, controller: Dict, devices: List):
        """Recursively extract device info"""
        
        if 'usb_device' in controller:
            for device in controller.get('usb_device', []):
                device_info = {
                    'name': device.get('_name', 'Unknown Device'),
                    'product_id': device.get('product_id', 'Unknown'),
                    'vendor_id': device.get('vendor_id', 'Unknown'),
                    'serial': device.get('serial_num', 'Unknown'),
                    'speed': device.get('speed', 'Unknown'),
                    'manufacturer': device.get('manufacturer_name', 'Unknown'),
                    'device_type': self._classify_device(device),
                    'bus_type': 'USB',
                }
                devices.append(device_info)
                
                # Recursively process nested devices
                if 'usb_device' in device:
                    self._extract_devices_from_controller(device, devices)
    
    def get_storage_devices(self) -> List[Dict]:
        """Get USB storage devices with mount information"""
        devices = []
        
        try:
            # Get disk list
            result = subprocess.run(
                ['diskutil', 'list', '-plist'],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                plist_data = plistlib.loads(result.stdout)
                devices = self._parse_diskutil_output(plist_data)
        
        except Exception as e:
            print(f"Error querying storage devices: {e}")
        
        return devices
    
    def _parse_diskutil_output(self, plist_data: Dict) -> List[Dict]:
        """Parse diskutil plist output"""
        devices = []
        
        try:
            all_disks_and_partitions = plist_data.get('AllDisksAndPartitions', [])
            
            for disk in all_disksandpartitions:
                disk_identifier = disk.get('Disk')
                
                # Check if this is a USB device
                if self._is_usb_disk(disk_identifier):
                    
                    for partition in disk.get('Partitions', []):
                        device_info = {
                            'name': partition.get('VolumeName', 'Untitled'),
                            'mount_point': partition.get('MountPoint'),
                            'device_type': 'STORAGE',
                            'file_system': partition.get('FilesystemType'),
                            'device_path': f"/dev/{partition.get('DeviceIdentifier')}",
                            'size': partition.get('Size', 0),
                        }
                        
                        if device_info['mount_point']:
                            devices.append(device_info)
        
        except Exception as e:
            print(f"Error parsing disk info: {e}")
        
        return devices
    
    def _is_usb_disk(self, disk_identifier: str) -> bool:
        """Check if disk is USB-connected"""
        try:
            result = subprocess.run(
                ['diskutil', 'info', '-plist', disk_identifier],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                disk_info = plistlib.loads(result.stdout)
                
                # Check for USB in device information
                bus_protocol = disk_info.get('BusProtocol', '')
                device_name = disk_info.get('DeviceName', '')
                
                return 'USB' in bus_protocol.upper() or 'USB' in device_name.upper()
        
        except:
            pass
        
        return False
    
    def get_device_by_mount_point(self, mount_point: str) -> Dict:
        """Get device info by mount point"""
        try:
            result = subprocess.run(
                ['diskutil', 'info', '-plist', mount_point],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                disk_info = plistlib.loads(result.stdout)
                
                return {
                    'name': disk_info.get('VolumeNickname'),
                    'mount_point': mount_point,
                    'file_system': disk_info.get('FilesystemType'),
                    'device_path': disk_info.get('DeviceNode'),
                    'total_bytes': disk_info.get('TotalSize', 0),
                    'free_bytes': disk_info.get('FreeSpace', 0),
                }
        
        except Exception as e:
            print(f"Error getting device info: {e}")
        
        return None
    
    @staticmethod
    def _classify_device(device: Dict) -> str:
        """Classify device type"""
        name = device.get('_name', '').upper()
        
        if 'STORAGE' in name or 'DRIVE' in name:
            return 'STORAGE'
        elif 'AUDIO' in name or 'SPEAKER' in name or 'HEADPHONE' in name:
            return 'AUDIO'
        elif 'CAMERA' in name or 'WEBCAM' in name:
            return 'CAMERA'
        elif 'KEYBOARD' in name or 'MOUSE' in name:
            return 'INPUT'
        elif 'PRINTER' in name:
            return 'PRINTER'
        
        return 'GENERIC'
```

### 2. File Operations for Speed Testing

```python
# macOS implementation is similar to Linux (POSIX-based)

class MacOSSpeedTester:
    """macOS-specific speed test implementation"""
    
    def __init__(self):
        self.test_file_name = "__usb_speedtest_temp__.dat"
    
    def write_test(self, mount_point: str, size_mb: int = 100) -> Tuple[float, float]:
        """
        Perform write speed test
        mount_point: e.g., "/Volumes/USB_DRIVE"
        """
        test_file_path = os.path.join(mount_point, self.test_file_name)
        chunk_size = 1024 * 1024  # 1 MB
        total_size = size_mb * 1024 * 1024
        
        start_time = time.perf_counter()
        bytes_written = 0
        
        try:
            with open(test_file_path, 'wb', buffering=0) as f:
                while bytes_written < total_size:
                    chunk = os.urandom(chunk_size)
                    f.write(chunk)
                    bytes_written += len(chunk)
                
                # Force flush using fcntl
                os.fsync(f.fileno())
        
        except IOError as e:
            raise Exception(f"Write test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_written, duration
    
    def read_test(self, file_path: str) -> Tuple[float, float]:
        """Perform read speed test"""
        chunk_size = 1024 * 1024
        start_time = time.perf_counter()
        bytes_read = 0
        
        try:
            with open(file_path, 'rb', buffering=0) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
        
        except IOError as e:
            raise Exception(f"Read test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_read, duration
    
    def cleanup(self, mount_point: str):
        """Remove temporary test file"""
        test_file_path = os.path.join(mount_point, self.test_file_name)
        
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file: {e}")
```

### 3. Default Data Directory

```python
# config.py - macOS paths

from pathlib import Path

MACOS_BASE_DIR = Path.home() / "Library" / "Application Support" / "USBSpeedTest"

MACOS_PATHS = {
    'data_dir': MACOS_BASE_DIR,
    'reports_dir': MACOS_BASE_DIR / "reports",
    'logs_dir': MACOS_BASE_DIR / "logs",
    'config_file': MACOS_BASE_DIR / "config.json",
    'cache_file': MACOS_BASE_DIR / "cache.json",
}

def ensure_macos_directories():
    """Create required macOS directories"""
    for directory in [
        MACOS_PATHS['data_dir'],
        MACOS_PATHS['reports_dir'],
        MACOS_PATHS['logs_dir'],
    ]:
        directory.mkdir(parents=True, exist_ok=True)
```

### 4. System Notifications (macOS)

```python
# modules/monitor_service.py - macOS notifications

import subprocess

class MacOSNotificationManager:
    """macOS notification using osascript"""
    
    def show_notification(self, title: str, message: str):
        """Show system notification using AppleScript"""
        
        apple_script = f'''
        display notification "{message}" with title "{title}"
        '''
        
        try:
            subprocess.run(
                ['osascript', '-e', apple_script],
                check=True,
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")
```

### 5. Tray Icon (macOS)

```python
# Similar to Windows using pystray, but macOS has native menu bar integration

class MacOSTrayIcon:
    """macOS menu bar icon integration"""
    
    # Implementation similar to Windows
    # pystray handles macOS menu bar automatically
```

---

## Linux Implementation

### 1. USB Device Detection

```python
# modules/usb_detector.py - Linux implementation

import subprocess
import json
import os
from typing import List, Dict

class LinuxDeviceDetector:
    """Detect USB devices on Linux"""
    
    def get_all_usb_devices(self) -> List[Dict]:
        """Get all USB devices using lsusb"""
        devices = []
        
        try:
            # Use lsusb to enumerate USB devices
            result = subprocess.run(
                ['lsusb', '-v', '-j'],  # JSON output if available (newer lsusb)
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                devices = self._parse_lsusb_json(result.stdout)
            else:
                # Fallback to parsing text output
                devices = self._parse_lsusb_text()
        
        except FileNotFoundError:
            # Fallback to /sys enumeration
            devices = self._detect_via_sysfs()
        
        except Exception as e:
            print(f"Error querying USB devices: {e}")
        
        return devices
    
    def _parse_lsusb_json(self, json_output: str) -> List[Dict]:
        """Parse JSON output from lsusb"""
        devices = []
        
        try:
            data = json.loads(json_output)
            
            for device in data.get('devices', []):
                device_info = {
                    'vendor_id': f"{device.get('idVendor', 0):04x}",
                    'product_id': f"{device.get('idProduct', 0):04x}",
                    'name': device.get('iProduct', 'Unknown Device'),
                    'manufacturer': device.get('iManufacturer', 'Unknown'),
                    'serial': device.get('iSerialNumber'),
                    'bus_num': device.get('busnum'),
                    'dev_num': device.get('devnum'),
                    'speed': device.get('speed'),
                    'max_power': device.get('bMaxPower'),
                    'device_type': self._classify_by_class(device),
                    'bus_type': 'USB',
                }
                devices.append(device_info)
        
        except json.JSONDecodeError as e:
            print(f"Error parsing lsusb JSON: {e}")
        
        return devices
    
    def _detect_via_sysfs(self) -> List[Dict]:
        """Fallback: enumerate USB devices via /sys/class/usb_device"""
        devices = []
        
        try:
            usb_class_path = '/sys/class/usb_device'
            
            if not os.path.exists(usb_class_path):
                usb_class_path = '/sys/bus/usb/devices'
            
            for device_name in os.listdir(usb_class_path):
                device_path = os.path.join(usb_class_path, device_name)
                
                device_info = {
                    'name': self._read_sysfs_attr(device_path, 'product', 'Unknown'),
                    'manufacturer': self._read_sysfs_attr(device_path, 'manufacturer', 'Unknown'),
                    'serial': self._read_sysfs_attr(device_path, 'serial', 'Unknown'),
                    'vendor_id': self._read_sysfs_attr(device_path, 'idVendor'),
                    'product_id': self._read_sysfs_attr(device_path, 'idProduct'),
                    'device_type': self._read_sysfs_attr(device_path, 'bDeviceClass'),
                    'device_path': device_path,
                    'bus_type': 'USB',
                }
                
                devices.append(device_info)
        
        except Exception as e:
            print(f"Error reading sysfs: {e}")
        
        return devices
    
    def get_storage_devices(self) -> List[Dict]:
        """Get USB storage devices with mount points"""
        devices = []
        
        try:
            # Use lsblk to find USB storage devices
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,MOUNTPOINT,SIZE,TYPE,FSTYPE,SERIAL'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                devices = self._parse_lsblk_output(data)
        
        except FileNotFoundError:
            devices = self._detect_storage_via_sysfs()
        
        except Exception as e:
            print(f"Error querying storage devices: {e}")
        
        return devices
    
    def _parse_lsblk_output(self, data: Dict) -> List[Dict]:
        """Parse lsblk JSON output"""
        devices = []
        
        def process_block_device(device: Dict, parent_name: str = None):
            """Recursively process block devices"""
            
            # Check if this is a USB device (heuristic)
            device_name = device.get('name', '')
            is_removable = self._is_usb_device(device_name)
            
            if is_removable and device.get('mountpoint'):
                device_info = {
                    'name': device_name,
                    'mount_point': device.get('mountpoint'),
                    'device_type': 'STORAGE',
                    'file_system': device.get('fstype'),
                    'size': self._parse_size(device.get('size', '0')),
                    'serial': device.get('serial'),
                    'device_path': f'/dev/{device_name}',
                }
                devices.append(device_info)
            
            # Process children
            for child in device.get('children', []):
                process_block_device(child, device_name)
        
        for device in data.get('blockdevices', []):
            process_block_device(device)
        
        return devices
    
    def _is_usb_device(self, device_name: str) -> bool:
        """Check if device is USB-connected"""
        try:
            device_path = f'/sys/block/{device_name}/device'
            
            if os.path.islink(device_path):
                real_path = os.path.realpath(device_path)
                return 'usb' in real_path
        except:
            pass
        
        return False
    
    @staticmethod
    def _read_sysfs_attr(device_path: str, attr_name: str, default: str = 'Unknown') -> str:
        """Read attribute from sysfs"""
        try:
            attr_path = os.path.join(device_path, attr_name)
            
            if os.path.exists(attr_path):
                with open(attr_path, 'r') as f:
                    return f.read().strip()
        except:
            pass
        
        return default
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parse size string to bytes"""
        if not size_str:
            return 0
        
        units = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
        
        for unit, multiplier in units.items():
            if unit in size_str.upper():
                try:
                    return int(float(size_str.upper().replace(unit, '')) * multiplier)
                except:
                    return 0
        
        return int(size_str) if size_str.isdigit() else 0
    
    @staticmethod
    def _classify_by_class(device: Dict) -> str:
        """Classify device by USB class"""
        bDeviceClass = device.get('bDeviceClass', 0)
        
        class_map = {
            0x01: 'AUDIO',
            0x03: 'INPUT',
            0x06: 'IMAGE',  # Camera
            0x07: 'PRINTER',
            0x08: 'STORAGE',
            0x09: 'HUB',
            0xFF: 'VENDOR',
        }
        
        return class_map.get(bDeviceClass, 'GENERIC')
    
    def _detect_storage_via_sysfs(self) -> List[Dict]:
        """Fallback storage detection via /sys"""
        devices = []
        
        try:
            block_path = '/sys/block'
            
            for device_name in os.listdir(block_path):
                if self._is_usb_device(device_name):
                    device_info = {
                        'name': device_name,
                        'device_path': f'/dev/{device_name}',
                        'device_type': 'STORAGE',
                        'is_removable': self._is_removable(device_name),
                    }
                    devices.append(device_info)
        
        except Exception as e:
            print(f"Error reading block devices: {e}")
        
        return devices
    
    @staticmethod
    def _is_removable(device_name: str) -> bool:
        """Check if device is marked as removable"""
        try:
            removable_path = f'/sys/block/{device_name}/removable'
            
            with open(removable_path, 'r') as f:
                return f.read().strip() == '1'
        except:
            return False
```

### 2. File Operations for Speed Testing

```python
# modules/speed_test.py - Linux implementation (POSIX)

class LinuxSpeedTester:
    """Linux-specific speed test implementation"""
    
    def __init__(self):
        self.test_file_name = "__usb_speedtest_temp__.dat"
    
    def write_test(self, mount_point: str, size_mb: int = 100) -> Tuple[float, float]:
        """
        Perform write speed test on Linux mount point
        """
        test_file_path = os.path.join(mount_point, self.test_file_name)
        chunk_size = 1024 * 1024  # 1 MB
        total_size = size_mb * 1024 * 1024
        
        start_time = time.perf_counter()
        bytes_written = 0
        
        try:
            with open(test_file_path, 'wb', buffering=0) as f:
                while bytes_written < total_size:
                    chunk = os.urandom(chunk_size)
                    bytes_written += f.write(chunk)
                
                # Sync to disk
                os.fsync(f.fileno())
        
        except IOError as e:
            raise Exception(f"Write test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_written, duration
    
    def read_test(self, file_path: str) -> Tuple[float, float]:
        """Perform read speed test"""
        chunk_size = 1024 * 1024
        start_time = time.perf_counter()
        bytes_read = 0
        
        try:
            with open(file_path, 'rb', buffering=0) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
        
        except IOError as e:
            raise Exception(f"Read test failed: {e}")
        
        finally:
            duration = time.perf_counter() - start_time
        
        return bytes_read, duration
    
    def cleanup(self, mount_point: str):
        """Remove temporary test file"""
        test_file_path = os.path.join(mount_point, self.test_file_name)
        
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file: {e}")
```

### 3. Default Data Directory

```python
# config.py - Linux paths

from pathlib import Path

LINUX_BASE_DIR = Path.home() / ".local" / "share" / "usb-speedtest"

LINUX_PATHS = {
    'data_dir': LINUX_BASE_DIR,
    'reports_dir': LINUX_BASE_DIR / "reports",
    'logs_dir': LINUX_BASE_DIR / "logs",
    'config_file': LINUX_BASE_DIR / "config.json",
    'cache_file': LINUX_BASE_DIR / "cache.json",
}

def ensure_linux_directories():
    """Create required Linux directories"""
    for directory in [
        LINUX_PATHS['data_dir'],
        LINUX_PATHS['reports_dir'],
        LINUX_PATHS['logs_dir'],
    ]:
        directory.mkdir(parents=True, exist_ok=True)
```

### 4. System Notifications (Linux)

```python
# modules/monitor_service.py - Linux notifications

import subprocess

class LinuxNotificationManager:
    """Linux D-Bus notification system"""
    
    def show_notification(self, title: str, message: str, urgency: str = 'normal'):
        """Show system notification using notify-send"""
        
        urgency_map = {'low': '0', 'normal': '1', 'high': '2'}
        
        try:
            subprocess.run(
                [
                    'notify-send',
                    '-u', urgency_map.get(urgency, '1'),
                    title,
                    message
                ],
                check=True,
                capture_output=True,
                timeout=5
            )
        except FileNotFoundError:
            print("notify-send not found. Install libnotify-bin.")
        except Exception as e:
            print(f"Failed to show notification: {e}")
```

### 5. Tray Icon (Linux)

```python
# Linux tray icon using pystray
# Implementation is platform-agnostic with pystray
```

---

## Cross-Platform Abstraction Layer

### platform_utils.py

```python
# utils/platform_utils.py

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict

class PlatformUtils:
    """Unified interface for cross-platform operations"""
    
    @staticmethod
    def get_platform() -> str:
        """Return current platform identifier"""
        if sys.platform == 'win32':
            return 'windows'
        elif sys.platform == 'darwin':
            return 'macos'
        elif sys.platform.startswith('linux'):
            return 'linux'
        else:
            return 'unknown'
    
    @staticmethod
    def get_app_data_dir() -> Path:
        """Get platform-specific data directory"""
        platform = PlatformUtils.get_platform()
        
        if platform == 'windows':
            return Path("C:\\ProgramData\\UBSSpeedTest")
        elif platform == 'macos':
            return Path.home() / "Library" / "Application Support" / "USBSpeedTest"
        else:  # Linux
            return Path.home() / ".local" / "share" / "usb-speedtest"
    
    @staticmethod
    def get_device_detector():
        """Factory method for platform-specific device detector"""
        platform = PlatformUtils.get_platform()
        
        if platform == 'windows':
            from modules.usb_detector import WindowsDeviceDetector
            return WindowsDeviceDetector()
        elif platform == 'macos':
            from modules.usb_detector import MacOSDeviceDetector
            return MacOSDeviceDetector()
        else:  # Linux
            from modules.usb_detector import LinuxDeviceDetector
            return LinuxDeviceDetector()
    
    @staticmethod
    def get_speed_tester():
        """Factory method for platform-specific speed tester"""
        platform = PlatformUtils.get_platform()
        
        if platform == 'windows':
            from modules.speed_test import WindowsSpeedTester
            return WindowsSpeedTester()
        elif platform == 'macos':
            from modules.speed_test import MacOSSpeedTester
            return MacOSSpeedTester()
        else:  # Linux
            from modules.speed_test import LinuxSpeedTester
            return LinuxSpeedTester()
    
    @staticmethod
    def get_notification_manager():
        """Factory method for platform-specific notifications"""
        platform = PlatformUtils.get_platform()
        
        if platform == 'windows':
            from modules.monitor_service import WindowsNotificationManager
            return WindowsNotificationManager()
        elif platform == 'macos':
            from modules.monitor_service import MacOSNotificationManager
            return MacOSNotificationManager()
        else:  # Linux
            from modules.monitor_service import LinuxNotificationManager
            return LinuxNotificationManager()
    
    @staticmethod
    def open_file_in_browser(file_path: str) -> bool:
        """Open file in default browser/viewer"""
        import webbrowser
        
        try:
            webbrowser.open(f'file://{os.path.abspath(file_path)}')
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
    
    @staticmethod
    def open_file_explorer(path: str) -> bool:
        """Open path in file explorer"""
        platform = PlatformUtils.get_platform()
        
        try:
            if platform == 'windows':
                import subprocess
                subprocess.Popen(f'explorer /select,"{path}"')
            elif platform == 'macos':
                import subprocess
                subprocess.Popen(['open', '-R', path])
            else:  # Linux
                import subprocess
                subprocess.Popen(['xdg-open', os.path.dirname(path)])
            
            return True
        except Exception as e:
            print(f"Error opening file explorer: {e}")
            return False
```

---

## Testing on Each Platform

### Windows Testing Checklist

- [ ] Install Python 3.9+ and required packages
- [ ] Run `python main.py` to launch application
- [ ] List USB devices and verify all detected
- [ ] Run speed test on USB drive (C:\ProgramData\UBSSpeedTest\)
- [ ] Check HTML report generation
- [ ] Test background monitoring notifications
- [ ] Build with PyInstaller and test executable
- [ ] Test with multiple USB devices simultaneously
- [ ] Verify unmount/remount device handling

### macOS Testing Checklist

- [ ] Install Python 3.9+ via Homebrew or .pkg
- [ ] Install system_profiler, diskutil utilities
- [ ] Grant accessibility permissions for tray icon
- [ ] Run application and test device enumeration
- [ ] Verify USB speed test functionality
- [ ] Test report generation
- [ ] Check system notifications
- [ ] Build DMG installer
- [ ] Test on both Intel and Apple Silicon (M1+)

### Linux Testing Checklist

- [ ] Install Python 3.9+ and system packages:
  - Ubuntu/Debian: `sudo apt install python3-dev lsusb libnotify-bin`
  - Red Hat/CentOS: `sudo yum install python3-devel lsusb libnotify`
- [ ] Verify `/sys/class/block` and `/proc/mounts` access
- [ ] Test USB device detection
- [ ] Run speed benchmark
- [ ] Check notification display
- [ ] Build AppImage package
- [ ] Test on Ubuntu, Debian, and one ARM-based distro (Raspberry Pi)

---

**End of Platform-Specific Implementation Guide**
