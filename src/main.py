import os
import sys
import uuid
import datetime
import threading
import psutil
import webview

# Path fixes
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "modules"))

from config import REPORTS_DIR, BASE_DIR, load_config, save_config
from modules.usb_detector import get_usb_storage_devices, get_usb_peripherals
from modules.speed_test import perform_speed_test, generate_html_report, generate_comparison_html_report
from modules.platform_utils import get_platform, open_report_file, open_file_explorer
from modules.ai_client import AIClient
import modules.monitor_service as monitor_service

# Global State
app_window = None
test_history = []
cancel_requested = False

class BackendAPI:
    def __init__(self):
        self.session_id = f"session-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        self.session_start = datetime.datetime.now().isoformat() + "Z"

    # API Standard Response Formatter
    def _response(self, success, data=None, error=None):
        return {
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.datetime.now().isoformat() + "Z"
        }

    # 1. Get All Connected Devices
    def get_all_devices(self):
        try:
            storage = self.get_storage_devices()
            peripherals = self.get_peripheral_devices()
            all_devs = []
            
            if storage["success"] and storage["data"]:
                all_devs.extend(storage["data"]["devices"])
            if peripherals["success"] and peripherals["data"]:
                all_devs.extend(peripherals["data"]["devices"])
                
            return self._response(True, {
                "total_devices": len(all_devs),
                "devices": all_devs
            })
        except Exception as e:
            return self._response(False, error=f"Failed to enumerate USB devices: {e}")

    # 2. Get Storage Devices Only
    def get_storage_devices(self):
        try:
            raw_storage = get_usb_storage_devices()
            devices = []
            
            for dev in raw_storage:
                vol_info = dev["volumes"][0] if dev["volumes"] else {}
                total_gb = round(vol_info.get("total", 0) / (1024**3), 2)
                free_gb = round(vol_info.get("free", 0) / (1024**3), 2)
                used_gb = round(vol_info.get("used", 0) / (1024**3), 2)
                
                devices.append({
                    "id": dev["id"],
                    "name": dev["model"],
                    "vendor": dev["model"].split()[0] if dev["model"] else "Generic",
                    "product_id": "N/A",
                    "vendor_id": "N/A",
                    "serial": dev["serial"],
                    "device_type": "STORAGE",
                    "bus_type": "USB",
                    "is_removable": True,
                    "mount_point": vol_info.get("mount_point"),
                    "file_system": vol_info.get("file_system", "FAT32"),
                    "total_space_gb": total_gb,
                    "used_space_gb": used_gb,
                    "free_space_gb": free_gb,
                    "percent_used": round((used_gb / total_gb) * 100, 1) if total_gb > 0 else 0,
                    "is_mounted": len(dev["volumes"]) > 0
                })
                
            return self._response(True, {
                "total_storage_devices": len(devices),
                "devices": devices
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 3. Get Peripheral Devices Only
    def get_peripheral_devices(self):
        try:
            raw_per = get_usb_peripherals()
            devices = []
            
            for per in raw_per:
                devices.append({
                    "id": f"usb-per-{uuid.uuid4().hex[:4]}",
                    "name": per["name"],
                    "vendor": per["name"].split()[0] if per["name"] else "Generic",
                    "device_type": per["class"].upper(),
                    "speed": "USB 2.0/3.0",
                    "protocol": per["class"],
                    "is_removable": True,
                    "mount_point": None
                })
                
            return self._response(True, {
                "total_peripheral_devices": len(devices),
                "devices": devices
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 4. Get Devices by Type
    def get_devices_by_type(self, device_type):
        try:
            all_res = self.get_all_devices()
            if not all_res["success"]:
                return all_res
                
            filtered = [d for d in all_res["data"]["devices"] if d["device_type"] == device_type.upper()]
            return self._response(True, {
                "device_type": device_type,
                "count": len(filtered),
                "devices": filtered
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 5. Get Device Details
    def get_device_details(self, device_id):
        try:
            all_res = self.get_all_devices()
            if not all_res["success"]:
                return all_res
                
            for d in all_res["data"]["devices"]:
                if d["id"] == device_id:
                    # Enrich details
                    if d["device_type"] == "STORAGE":
                        d["total_space_bytes"] = int(d["total_space_gb"] * (1024**3))
                        d["used_space_bytes"] = int(d["used_space_gb"] * (1024**3))
                        d["free_space_bytes"] = int(d["free_space_gb"] * (1024**3))
                    return self._response(True, d)
            return self._response(False, error="Device not found")
        except Exception as e:
            return self._response(False, error=str(e))

    # 6. Get Space Info
    def get_space_info(self, device_id):
        try:
            details_res = self.get_device_details(device_id)
            if not details_res["success"]:
                return details_res
                
            d = details_res["data"]
            if d["device_type"] != "STORAGE":
                return self._response(False, error="Device is not a storage unit")
                
            return self._response(True, {
                "device_id": d["id"],
                "device_name": d["name"],
                "total_bytes": d.get("total_space_bytes", 0),
                "total_gb": d["total_space_gb"],
                "used_bytes": d.get("used_space_bytes", 0),
                "used_gb": d["used_space_gb"],
                "free_bytes": d.get("free_space_bytes", 0),
                "free_gb": d["free_space_gb"],
                "percent_used": d["percent_used"],
                "percent_free": round(100 - d["percent_used"], 1),
                "file_system": d["file_system"],
                "mount_point": d["mount_point"]
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 7. Run Speed Test
    def run_speed_test(self, device_id, test_size_mb=100):
        global cancel_requested, test_history
        cancel_requested = False
        
        try:
            details_res = self.get_device_details(device_id)
            if not details_res["success"]:
                return details_res
                
            d = details_res["data"]
            mount_point = d.get("mount_point")
            if not mount_point:
                return self._response(False, error="Mount point not available for test")
                
            # Progress callback checking for cancel
            def progress_cb(stage, pct, current_speed):
                global cancel_requested
                if cancel_requested:
                    raise Exception("Speed test cancelled by user")
                    
                if app_window:
                    app_window.evaluate_js(f"window.updateTestProgress('{stage}', {pct}, {current_speed});")

            results = perform_speed_test(mount_point, test_file_size_mb=test_size_mb, progress_callback=progress_cb)
            
            # Save report
            volume_info = {
                "mount_point": mount_point,
                "file_system": d["file_system"],
                "total": int(d["total_space_gb"] * (1024**3)),
                "free": int(d["free_space_gb"] * (1024**3)),
                "used": int(d["used_space_gb"] * (1024**3))
            }
            device_info = {
                "model": d["name"],
                "serial": d["serial"],
                "id": d["id"]
            }
            report_path = generate_html_report(device_info, volume_info, results)
            
            test_id = f"test-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            test_result = {
                "test_id": test_id,
                "device_id": device_id,
                "device_name": d["name"],
                "device_path": mount_point,
                "file_system": d["file_system"],
                "test_size_mb": test_size_mb,
                "test_duration_sec": results["write_duration"] + results["read_duration"],
                "write_speed_mbps": results["write_speed"],
                "read_speed_mbps": results["read_speed"],
                "write_duration_sec": results["write_duration"],
                "read_duration_sec": results["read_duration"],
                "timestamp": datetime.datetime.now().isoformat() + "Z",
                "space_info": {
                    "total_space_gb": d["total_space_gb"],
                    "used_space_gb": d["used_space_gb"],
                    "free_space_gb": d["free_space_gb"],
                    "percent_used": d["percent_used"]
                },
                "report_path": report_path
            }
            
            test_history.append(test_result)
            return self._response(True, test_result)
            
        except Exception as e:
            if "cancelled" in str(e).lower():
                return self._response(False, error="Speed test cancelled successfully")
            return self._response(False, error=f"Speed test failed: {e}")

    # 8. Get Test History
    def get_test_history(self):
        return self._response(True, {
            "session_id": self.session_id,
            "session_start_time": self.session_start,
            "total_tests": len(test_history),
            "tests": test_history
        })

    # 9. Cancel Speed Test
    def cancel_speed_test(self):
        global cancel_requested
        cancel_requested = True
        return self._response(True, {"message": "Cancellation request registered"})

    # 10. Generate Device Report
    def generate_device_report(self, test_id):
        for test in test_history:
            if test["test_id"] == test_id:
                return self._response(True, {
                    "report_id": f"report-{test_id[5:]}",
                    "report_path": test["report_path"],
                    "file_size_bytes": os.path.getsize(test["report_path"]) if os.path.exists(test["report_path"]) else 0,
                    "generated_timestamp": datetime.datetime.now().isoformat() + "Z",
                    "device_name": test["device_name"],
                    "test_date": test["timestamp"]
                })
        return self._response(False, error="Test result not found in session")

    # 11. Generate Comparison Report
    def generate_comparison_report(self, test_ids):
        # Format the parameters for the standard generator
        runs_to_compare = []
        for tid in test_ids:
            for test in test_history:
                if test["test_id"] == tid:
                    runs_to_compare.append({
                        "device": { "model": test["device_name"], "serial": "N/A", "id": test["device_id"] },
                        "volume": { "mount_point": test["device_path"], "file_system": test["file_system"] },
                        "results": {
                            "read_speed": test["read_speed_mbps"],
                            "write_speed": test["write_speed_mbps"],
                            "test_size_mb": test["test_size_mb"],
                            "read_duration": test["read_duration_sec"],
                            "write_duration": test["write_duration_sec"]
                        }
                    })
                    break
        try:
            report_path = generate_comparison_html_report(runs_to_compare)
            if report_path:
                return self._response(True, {
                    "report_id": f"compare-{uuid.uuid4().hex[:6]}",
                    "report_path": report_path,
                    "file_size_bytes": os.path.getsize(report_path) if os.path.exists(report_path) else 0,
                    "generated_timestamp": datetime.datetime.now().isoformat() + "Z",
                    "compared_tests_count": len(test_ids),
                    "devices_compared": [r["device"]["model"] for r in runs_to_compare]
                })
            return self._response(False, error="No valid tests to compare")
        except Exception as e:
            return self._response(False, error=str(e))

    # 12. Get Reports List
    def get_reports_list(self, limit=50):
        try:
            reports = []
            if REPORTS_DIR.exists():
                for filename in os.listdir(REPORTS_DIR):
                    if filename.endswith(".html"):
                        path = REPORTS_DIR / filename
                        created = datetime.datetime.fromtimestamp(os.path.getctime(path)).isoformat() + "Z"
                        reports.append({
                            "report_id": f"report-file-{uuid.uuid4().hex[:4]}",
                            "report_type": "comparison" if "compare" in filename else "device",
                            "file_name": filename,
                            "file_path": str(path),
                            "file_size_bytes": os.path.getsize(path),
                            "created_timestamp": created,
                            "device_name": filename.split("_")[1] if "_" in filename else "Benchmark"
                        })
            # Sort reports by creation time descending
            reports.sort(key=lambda x: x["created_timestamp"], reverse=True)
            return self._response(True, {
                "total_reports": len(reports),
                "reports": reports[:limit]
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 13. Open Report
    def open_report(self, report_path):
        success = open_report_file(report_path)
        return self._response(success, {"message": "Report opened in default viewer"} if success else None, None if success else "Failed to open report")

    # 14. Get App Info
    def get_app_info(self):
        return self._response(True, {
            "app_name": "USB Speed Test & Monitor",
            "app_version": "1.1.0",
            "build_number": "20260606",
            "copyright": "2026",
            "platform": get_platform(),
            "data_directory": str(BASE_DIR),
            "config_file": str(BASE_DIR / "config.json")
        })

    # 15. Get System Info
    def get_system_info(self):
        try:
            mem = psutil.virtual_memory()
            return self._response(True, {
                "os_name": get_platform().capitalize(),
                "os_version": sys.platform,
                "os_build": sys.getwindowsversion().build if sys.platform == 'win32' else "N/A",
                "python_version": sys.version.split()[0],
                "pywebview_version": webview.__version__ if hasattr(webview, '__version__') else "Latest",
                "processor_count": psutil.cpu_count(),
                "total_memory_gb": round(mem.total / (1024**3), 2),
                "available_memory_gb": round(mem.available / (1024**3), 2)
            })
        except Exception as e:
            return self._response(False, error=str(e))

    # 16. Get Configuration
    def get_config(self):
        return self._response(True, load_config())

    # 17. Update Configuration
    def update_config(self, config_dict):
        success = save_config(config_dict)
        if success:
            # Propagate changes to services (e.g. restarts monitoring service with new interval if needed)
            if config_dict.get("monitoring", {}).get("enabled", True):
                monitor_service.start_monitoring()
            else:
                monitor_service.stop_monitoring()
            return self._response(True, {"message": "Configuration updated successfully"})
        return self._response(False, error="Failed to write configuration file")

    # 18. Open Path in File Explorer
    def open_path(self, path):
        success = open_file_explorer(path)
        return self._response(success, {"message": "Opened successfully"} if success else None, None if success else "Failed to open path")

    # 19. Send Chatbot Message
    def send_chatbot_message(self, chat_history):
        global test_history
        try:
            config = load_config()
            ai_settings = config.get("ai_chatbot", {})
            
            provider = ai_settings.get("provider", "ollama")
            api_key = ai_settings.get("api_key", "")
            model = ai_settings.get("model", "llama3")
            endpoint = ai_settings.get("endpoint", "http://localhost:11434")
            
            # Enrich system prompt with active context
            devices_data = self.get_all_devices()
            devices_summary = ""
            if devices_data["success"] and devices_data["data"]:
                devs = devices_data["data"]["devices"]
                devices_summary = "\n".join([
                    f"- Name: {d['name']}, Type: {d['device_type']}, Mount: {d.get('mount_point') or 'N/A'}, FileSystem: {d.get('file_system') or 'N/A'}, Size: {d.get('total_space_gb') or 'N/A'} GB (Free: {d.get('free_space_gb') or 'N/A'} GB)"
                    for d in devs
                ])
            
            recent_benchmarks = ""
            if test_history:
                recent_benchmarks = "\n".join([
                    f"- Run: {t['device_name']} on {t['device_path']}. Read: {t['read_speed_mbps']:.2f} MB/s, Write: {t['write_speed_mbps']:.2f} MB/s (File size: {t['test_size_mb']} MB, System: {t['file_system']})"
                    for t in test_history[-5:]
                ])
            else:
                recent_benchmarks = "No speed benchmarks have been run in this session yet."
                
            system_prompt = (
                "You are the USB Speed Utility AI Assistant, a helpful and technical assistant integrated directly into a desktop USB diagnostics tool.\n"
                "Your goal is to help users analyze speed test results, explain USB hardware protocols/standards, and troubleshoot USB-related issues.\n\n"
                "Current System Context:\n"
                f"Connected USB Devices:\n{devices_summary or 'No USB devices detected.'}\n\n"
                f"Recent Benchmark Runs in this Session:\n{recent_benchmarks}\n\n"
                "Guidelines:\n"
                "1. Give direct, practical, technical yet easy-to-understand explanations.\n"
                "2. Suggest actionable steps if a device appears slow (e.g., check port types USB 2.0 vs 3.0, formatting options FAT32/exFAT/NTFS, cluster sizes).\n"
                "3. Keep answers concise, and format code or command instructions cleanly using Markdown blocks."
            )
            
            # Inject system prompt into history (remove any pre-existing system prompt to avoid conflict)
            full_history = [{"role": "system", "content": system_prompt}]
            for msg in chat_history:
                if msg["role"] != "system":
                    full_history.append(msg)
                    
            client = AIClient(provider, api_key, model, endpoint)
            reply = client.get_response(full_history)
            
            return self._response(True, {"reply": reply})
        except Exception as e:
            return self._response(False, error=str(e))

    # 20. Test LLM Connection
    def test_llm_connection(self, provider, api_key, model, endpoint):
        try:
            client = AIClient(provider, api_key, model, endpoint)
            test_history = [{"role": "user", "content": "Hello! Reply with exactly the word 'SUCCESS' and nothing else."}]
            reply = client.get_response(test_history)
            
            if reply:
                return self._response(True, {"reply": reply.strip()})
            return self._response(False, error="Received empty response from the provider.")
        except Exception as e:
            return self._response(False, error=str(e))


def show_app_window():
    if app_window:
        app_window.show()

def exit_app():
    monitor_service.stop_monitoring()
    if app_window:
        app_window.destroy()
    sys.exit(0)

def main():
    global app_window
    
    # Initialize Configuration folders
    ensure_directories = load_config()
    
    api = BackendAPI()
    
    # Set GUI Path
    if hasattr(sys, '_MEIPASS'):
        gui_dir = os.path.join(sys._MEIPASS, "gui")
    else:
        gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gui")
    index_html = os.path.abspath(os.path.join(gui_dir, "index.html"))
    
    # Start the monitoring service
    if ensure_directories.get("monitoring", {}).get("enabled", True):
        monitor_service.start_monitoring()
        
    tray_icon = monitor_service.setup_tray_icon(
        on_show_window=show_app_window,
        on_exit_app=exit_app
    )
    
    # Create the WebView Container
    app_window = webview.create_window(
        title='USB Speed Test & Monitor',
        url=index_html,
        js_api=api,
        width=1100,
        height=720,
        resizable=True,
        min_size=(900, 600)
    )
    
    webview.start()
    
    monitor_service.stop_monitoring()
    try:
        tray_icon.stop()
    except:
        pass

if __name__ == '__main__':
    main()
