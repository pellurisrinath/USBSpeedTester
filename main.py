import os
import sys
import threading
import webbrowser
import webview
import time

from usb_detector import get_usb_storage_devices, get_usb_peripherals
from speed_test import perform_speed_test, generate_html_report, generate_comparison_html_report
import monitor_service

# Global window reference
app_window = None

class BackendAPI:
    def __init__(self):
        self.monitoring_enabled = True

    def get_storage_devices(self):
        """Returns the list of USB storage devices connected."""
        return get_usb_storage_devices()

    def get_peripherals(self):
        """Returns the list of non-storage USB peripherals connected."""
        return get_usb_peripherals()

    def run_speed_test(self, device_id, mount_point, size_mb):
        """Runs the speed test on the selected mount point."""
        try:
            # Locate device model and other details for report
            devices = get_usb_storage_devices()
            target_device = None
            target_volume = None
            
            for dev in devices:
                if dev["id"] == device_id:
                    target_device = dev
                    for vol in dev["volumes"]:
                        if vol["mount_point"] == mount_point:
                            target_volume = vol
                            break
                    break
            
            if not target_device or not target_volume:
                return {"success": False, "error": "Selected device or mount point not found"}
            
            # Progress callback to trigger JS update
            def progress_cb(stage, pct, current_speed):
                if app_window:
                    # Execute JS in webview to update progress UI
                    app_window.evaluate_js(f"window.updateTestProgress('{stage}', {pct}, {current_speed});")

            # Run speed test benchmark (in the thread)
            results = perform_speed_test(mount_point, test_file_size_mb=size_mb, progress_callback=progress_cb)
            
            # Generate the detailed HTML report
            report_path = generate_html_report(target_device, target_volume, results)
            
            return {
                "success": True,
                "results": results,
                "report_path": report_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_comparison_report(self, test_runs):
        """Generates a side-by-side speed test comparison HTML report."""
        try:
            report_path = generate_comparison_html_report(test_runs)
            if report_path:
                return {"success": True, "report_path": report_path}
            else:
                return {"success": False, "error": "No test runs provided"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_html_report(self, path):
        """Opens the generated HTML report in the default system web browser."""
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(["open", path])
            else:
                import subprocess
                subprocess.run(["xdg-open", path])
            return True
        except Exception as e:
            print(f"Error opening report: {e}", file=sys.stderr)
            # Fallback to webbrowser
            try:
                webbrowser.open(f"file:///{path}")
                return True
            except:
                return False

    def toggle_monitoring_service(self, enabled):
        """Turns the low disk space monitoring service on or off."""
        self.monitoring_enabled = enabled
        if enabled:
            monitor_service.start_monitoring(interval=15)
        else:
            monitor_service.stop_monitoring()
        return enabled


def show_app_window():
    """Restores/shows the main app window."""
    if app_window:
        app_window.show()

def exit_app():
    """Stops services and shuts down the application."""
    monitor_service.stop_monitoring()
    if app_window:
        app_window.destroy()
    sys.exit(0)

def main():
    global app_window
    
    # Initialize backend API
    api = BackendAPI()
    
    # Set up GUI path
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui")
    index_html = os.path.join(gui_dir, "index.html")
    
    # Start the disk space background monitor service (checks every 15 seconds)
    monitor_service.start_monitoring(interval=15)
    
    # Set up and start the system tray icon
    tray_icon = monitor_service.setup_tray_icon(
        on_show_window=show_app_window,
        on_exit_app=exit_app
    )
    
    # Create the PyWebView Window
    app_window = webview.create_window(
        title='USB Speed Test & Monitor',
        url=index_html,
        js_api=api,
        width=1100,
        height=720,
        resizable=True,
        min_size=(900, 600)
    )
    
    # Run the Webview loop
    # On Windows, we override closed event to stop service and exit cleanly
    webview.start()
    
    # Clean up service on exit of the window loop
    monitor_service.stop_monitoring()
    try:
        tray_icon.stop()
    except:
        pass

if __name__ == '__main__':
    main()
