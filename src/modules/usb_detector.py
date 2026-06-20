import os
import sys
import subprocess
import json
import psutil
import plistlib

def get_usb_storage_devices():
    devices = []
    
    if sys.platform == 'win32':
        # On Windows, use PowerShell to get USB storage disks and partitions
        try:
            ps_script = """
            Get-Disk | Where-Object BusType -eq 'USB' | ForEach-Object {
                $disk = $_
                $parts = Get-Partition -DiskNumber $disk.Number
                $volumes = @()
                foreach ($part in $parts) {
                    if ($part.DriveLetter) {
                        try {
                            $vol = Get-Volume -DriveLetter $part.DriveLetter -ErrorAction Stop
                            $volumes += [PSCustomObject]@{
                                DriveLetter = $part.DriveLetter
                                Label = $vol.FileSystemLabel
                                Size = $vol.Size
                                FreeSpace = $vol.SizeRemaining
                                FileSystem = $vol.FileSystem
                            }
                        } catch {
                            # Volume might not be formatted or mounted properly
                        }
                    }
                }
                [PSCustomObject]@{
                    DiskNumber = $disk.Number
                    Model = $disk.FriendlyName
                    Size = $disk.Size
                    SerialNumber = $disk.SerialNumber
                    Volumes = $volumes
                }
            } | ConvertTo-Json -Depth 3
            """
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, check=True, creationflags=0x08000000)
            output = result.stdout.strip()
            
            if output:
                parsed = json.loads(output)
                # If parsed is a dict (single disk), wrap in a list
                if isinstance(parsed, dict):
                    disk_list = [parsed]
                else:
                    disk_list = parsed
                
                for disk in disk_list:
                    disk_info = {
                        "id": str(disk.get("DiskNumber")),
                        "model": disk.get("Model", "Unknown USB Disk"),
                        "size": disk.get("Size", 0),
                        "serial": disk.get("SerialNumber", "Unknown").strip(),
                        "volumes": []
                    }
                    
                    vols = disk.get("Volumes")
                    if vols:
                        if isinstance(vols, dict):
                            vols = [vols]
                        for vol in vols:
                            drive_letter = vol.get("DriveLetter")
                            mount_point = f"{drive_letter}:\\"
                            
                            # Get accurate size using psutil if possible
                            try:
                                usage = psutil.disk_usage(mount_point)
                                total = usage.total
                                free = usage.free
                                used = usage.used
                            except Exception:
                                total = vol.get("Size", 0)
                                free = vol.get("FreeSpace", 0)
                                used = total - free
                                
                            disk_info["volumes"].append({
                                "mount_point": mount_point,
                                "label": vol.get("Label", ""),
                                "file_system": vol.get("FileSystem", ""),
                                "total": total,
                                "free": free,
                                "used": used
                            })
                    devices.append(disk_info)
        except Exception as e:
            print(f"Error listing Windows USB storage: {e}", file=sys.stderr)
            
    elif sys.platform == 'darwin':
        # macOS implementation using diskutil and system_profiler Plist parsing
        try:
            cmd = ["diskutil", "list", "-plist"]
            res = subprocess.run(cmd, capture_output=True, check=True)
            plist_data = plistlib.loads(res.stdout)
            all_disks = plist_data.get('AllDisksAndPartitions', [])
            
            for disk in all_disks:
                disk_id = disk.get('Disk')
                if not disk_id:
                    continue
                
                # Verify if this is a USB disk using diskutil info -plist
                info_cmd = ["diskutil", "info", "-plist", disk_id]
                info_res = subprocess.run(info_cmd, capture_output=True)
                if info_res.returncode == 0:
                    info_data = plistlib.loads(info_res.stdout)
                    bus_protocol = info_data.get('BusProtocol', '')
                    device_name = info_data.get('DeviceName', '')
                    
                    if 'USB' in bus_protocol.upper() or 'USB' in device_name.upper():
                        disk_info = {
                            "id": disk_id,
                            "model": info_data.get('DeviceModel', 'USB Storage Device'),
                            "size": info_data.get('TotalSize', 0),
                            "serial": info_data.get('VolumeSerialNumber', 'Unknown'),
                            "volumes": []
                        }
                        
                        # Find mounted partitions
                        partitions = disk.get('Partitions', [])
                        for part in partitions:
                            mount = part.get('MountPoint')
                            if mount:
                                try:
                                    usage = psutil.disk_usage(mount)
                                    total = usage.total
                                    free = usage.free
                                    used = usage.used
                                except Exception:
                                    total = part.get('Size', 0)
                                    free = total
                                    used = 0
                                    
                                disk_info["volumes"].append({
                                    "mount_point": mount,
                                    "label": part.get('VolumeName', 'Untitled'),
                                    "file_system": part.get('Content', 'FAT32'),
                                    "total": total,
                                    "free": free,
                                    "used": used
                                })
                        
                        if disk_info["volumes"]:
                            devices.append(disk_info)
        except Exception as e:
            print(f"Error listing macOS USB storage: {e}", file=sys.stderr)
            
    elif sys.platform.startswith('linux'):
        # Linux implementation using lsblk
        try:
            cmd = ["lsblk", "-J", "-o", "NAME,FSTYPE,LABEL,MOUNTPOINT,SIZE,FSAVAIL,FSUSE%,MODEL,TRAN"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            
            for dev in data.get("blockdevices", []):
                # Check if device is USB or has USB partitions
                is_usb = dev.get("tran") == "usb"
                
                # Check children if any
                children_usb = False
                if dev.get("children"):
                    for child in dev.get("children", []):
                        if child.get("tran") == "usb":
                            children_usb = True
                            
                if is_usb or children_usb:
                    disk_info = {
                        "id": dev.get("name"),
                        "model": dev.get("model", "Unknown USB Disk"),
                        "size": dev.get("size", "0"),
                        "serial": "Unknown",
                        "volumes": []
                    }
                    
                    # Gather mount points
                    def parse_volumes(node):
                        vols = []
                        if node.get("mountpoint"):
                            try:
                                usage = psutil.disk_usage(node["mountpoint"])
                                vols.append({
                                    "mount_point": node["mountpoint"],
                                    "label": node.get("label", ""),
                                    "file_system": node.get("fstype", ""),
                                    "total": usage.total,
                                    "free": usage.free,
                                    "used": usage.used
                                })
                            except Exception:
                                pass
                        if node.get("children"):
                            for child in node["children"]:
                                vols.extend(parse_volumes(child))
                        return vols
                    
                    disk_info["volumes"] = parse_volumes(dev)
                    if disk_info["volumes"]:
                        devices.append(disk_info)
        except Exception as e:
            print(f"Error listing Linux USB storage: {e}", file=sys.stderr)
            
    return devices

def get_usb_peripherals():
    peripherals = []
    
    if sys.platform == 'win32':
        try:
            ps_script = """
            Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like 'USB*' -and $_.Class -ne 'DiskDrive' -and $_.Class -ne 'Volume' } | Select-Object FriendlyName, Class, InstanceId | ConvertTo-Json
            """
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, check=True, creationflags=0x08000000)
            output = result.stdout.strip()
            if output:
                parsed = json.loads(output)
                if isinstance(parsed, dict):
                    devices = [parsed]
                else:
                    devices = parsed
                
                for dev in devices:
                    name = dev.get("FriendlyName")
                    if name:
                        peripherals.append({
                            "name": name,
                            "class": dev.get("Class", "USB Device"),
                            "id": dev.get("InstanceId", "")
                        })
        except Exception as e:
            print(f"Error listing Windows USB peripherals: {e}", file=sys.stderr)
            
    elif sys.platform == 'darwin':
        try:
            # Parse system_profiler SPUSBDataType -json
            res = subprocess.run(['system_profiler', 'SPUSBDataType', '-json'], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                usb_info = data.get('SPUSBDataType', [])
                
                def extract_devices(node):
                    extracted = []
                    if isinstance(node, list):
                        for item in node:
                            extracted.extend(extract_devices(item))
                    elif isinstance(node, dict):
                        if '_name' in node:
                            name = node['_name']
                            dev_class = "USB Device"
                            if 'hub' in name.lower() or 'controller' in name.lower():
                                dev_class = "USB Hub"
                            extracted.append({
                                "name": name,
                                "class": dev_class,
                                "id": node.get('serial_num', '')
                            })
                        if 'usb_device' in node:
                            extracted.extend(extract_devices(node['usb_device']))
                    return extracted
                
                all_devs = extract_devices(usb_info)
                # Filter out generic hubs to keep peripherals list clean
                peripherals = [d for d in all_devs if d["class"] != "USB Hub"]
        except Exception as e:
            print(f"Error listing macOS USB peripherals: {e}", file=sys.stderr)
            
    elif sys.platform.startswith('linux'):
        try:
            # Parse lsusb
            result = subprocess.run(["lsusb"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.strip():
                    peripherals.append({
                        "name": line.strip(),
                        "class": "USB Device",
                        "id": ""
                    })
        except Exception as e:
            print(f"Error listing Linux USB peripherals: {e}", file=sys.stderr)
            
    return peripherals
