import os
import sys
import json
from pathlib import Path

# Base Directories
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent.resolve()
else:
    APP_DIR = Path(__file__).parent.parent.resolve()

# Check if application directory is writable (portable mode check)
is_portable = False
try:
    # Try creating a temporary test file in the app directory
    test_file = APP_DIR / ".write_test"
    test_file.touch()
    test_file.unlink()
    is_portable = True
except Exception:
    pass

if sys.platform == 'win32':
    BASE_DIR = Path("C:\\ProgramData\\USBSpeedTest")
elif is_portable:
    BASE_DIR = APP_DIR
else:
    if sys.platform == 'darwin':
        BASE_DIR = Path.home() / "Library" / "Application Support" / "USBSpeedTest"
    else:
        BASE_DIR = Path.home() / ".local" / "share" / "usb-speedtest"

REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "speed_test": {
        "default_test_size_mb": 100,
        "chunk_size_mb": 10,
        "timeout_seconds": 300,
        "enable_write_test": True,
        "enable_read_test": True
    },
    "monitoring": {
        "enabled": True,
        "check_interval_seconds": 60,
        "low_disk_threshold_percent": 10,
        "enable_notifications": True,
        "ignored_devices": []
    },
    "ui": {
        "theme": "dark",
        "auto_refresh_interval_ms": 5000,
        "show_all_devices": True
    },
    "reporting": {
        "auto_save": True,
        "include_charts": True,
        "include_device_history": True
    },
    "ai_chatbot": {
        "provider": "ollama",
        "api_key": "",
        "model": "llama3",
        "endpoint": "http://localhost:11434"
    }
}

def ensure_directories():
    """Ensures reports and logs folders exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """Loads configuration JSON from base directory, or writes default config if missing."""
    ensure_directories()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure keys exist (rudimentary merge)
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return DEFAULT_CONFIG

def save_config(config_dict):
    """Saves config dict to config.json."""
    ensure_directories()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}", file=sys.stderr)
        return False
