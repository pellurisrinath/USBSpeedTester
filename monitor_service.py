import os
import sys
import time
import threading
from PIL import Image, ImageDraw
import pystray
import psutil
from plyer import notification

from usb_detector import get_usb_storage_devices

# State for notifications (to prevent spamming the user)
notified_drives = set()

# Thread control
monitor_thread = None
monitoring_active = False

def create_tray_icon_image():
    """Generates a simple purple dot icon for the tray menu."""
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    # Draw a premium looking neon circle
    dc.ellipse((8, 8, 56, 56), fill=(139, 92, 246, 255), outline=(168, 85, 247, 255), width=2)
    dc.ellipse((20, 20, 44, 44), fill=(6, 182, 212, 255)) # info center
    return image

def send_system_notification(title, message):
    """Sends desktop notifications with native fallbacks on Mac/Linux."""
    try:
        # Try plyer first
        notification.notify(
            title=title,
            message=message,
            app_name="USB Speed Test",
            timeout=10
        )
    except Exception as e:
        print(f"Plyer notification failed, trying native fallbacks: {e}", file=sys.stderr)
        try:
            if sys.platform == 'darwin':
                # macOS Applescript notification fallback
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', script], check=True)
            elif sys.platform.startswith('linux'):
                # Linux notify-send fallback
                subprocess.run(['notify-send', title, message], check=True)
        except Exception as fallback_err:
            print(f"All notification methods failed: {fallback_err}", file=sys.stderr)

def check_low_disk_space():
    """Scans all USB drives and sends notifications for low disk space (<10%)."""
    global notified_drives
    try:
        import subprocess
        devices = get_usb_storage_devices()
        current_usb_mounts = set()
        
        for dev in devices:
            for vol in dev.get("volumes", []):
                mount = vol["mount_point"]
                current_usb_mounts.add(mount)
                
                total = vol["total"]
                free = vol["free"]
                
                if total > 0:
                    free_pct = (free / total) * 100
                    if free_pct < 10.0:
                        if mount not in notified_drives:
                            # Trigger low space alert
                            free_gb = round(free / (1024**3), 2)
                            dev_name = dev["model"]
                            
                            send_system_notification(
                                title="Low USB Storage Warning",
                                message=f"Drive {mount} ({dev_name}) is running low on space!\nOnly {free_gb} GB ({round(free_pct, 1)}%) free."
                            )
                            notified_drives.add(mount)
                    else:
                        # Reset if drive space is freed up
                        if mount in notified_drives:
                            notified_drives.remove(mount)
                            
        # Clean up removed drives from notified list
        notified_drives = notified_drives.intersection(current_usb_mounts)
        
    except Exception as e:
        print(f"Error during disk space monitoring: {e}", file=sys.stderr)

def monitor_loop(interval=30):
    """Loop running in background thread to monitor storage."""
    global monitoring_active
    while monitoring_active:
        check_low_disk_space()
        # Sleep in short increments to allow quick exit
        for _ in range(int(interval)):
            if not monitoring_active:
                break
            time.sleep(1)

def start_monitoring(interval=30):
    global monitor_thread, monitoring_active
    if not monitoring_active:
        monitoring_active = True
        monitor_thread = threading.Thread(target=monitor_loop, args=(interval,), daemon=True)
        monitor_thread.start()
        print("Storage monitoring service started.")

def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    print("Storage monitoring service stopped.")

def setup_tray_icon(on_show_window, on_exit_app):
    """Sets up the system tray icon using pystray."""
    image = create_tray_icon_image()
    
    def on_clicked(icon, item):
        if str(item) == "Open Speed Test":
            on_show_window()
        elif str(item) == "Exit":
            stop_monitoring()
            icon.stop()
            on_exit_app()
            
    menu = pystray.Menu(
        pystray.MenuItem("Open Speed Test", on_clicked),
        pystray.MenuItem("Exit", on_clicked)
    )
    
    icon = pystray.Icon("USBSpeedTest", image, "USB Speed Test & Monitor", menu)
    
    # Run tray icon in a separate thread so it doesn't block the main GUI loop
    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()
    return icon
