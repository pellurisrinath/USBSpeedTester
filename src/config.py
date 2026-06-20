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
COMPARISONS_DIR = BASE_DIR / "comparisions"
CONFIG_FILE = BASE_DIR / "config.json"
GUARDRAILS_FILE = BASE_DIR / "Guardrails.md"

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

def ensure_guardrails_file():
    """Ensures default Guardrails.md file exists in the BASE_DIR."""
    if not GUARDRAILS_FILE.exists():
        content = """# AI Assistant Guardrails

You must use these Guardrails as a strict pre-requisite when processing any user query.

1. **In-Scope Topics**: Only answer questions pertaining to the USB Speed Test & Monitor application, its features, USB technology, storage protocols, or hardware diagnostics and troubleshooting.
2. **Out-of-Scope Requests**: If the user asks about anything out of scope (such as generating images, generating PDFs, movies, writing general non-USB code, or general knowledge), you must NOT answer. Instead, respond with exactly: "This request is outside the scope of my usage as the USB Speed Utility AI Assistant."
3. **Email Templates**: You are allowed to write email templates only if the user specifically asks to report USB slowness, diagnostic results, or USB issues. You must NOT write general emails or general-purpose Python scripts for other projects. If asked for those, politely refuse or ask for more details on how it relates to USB diagnostics.
4. **Profanity Filter**: If the user uses any profane, vulgar, or inappropriate language, refuse to answer and state: "You have used a restricted word. This query will be marked and sent for review."
5. **Specs & Performance queries**: When asked about device specifications or performance, utilize the provided Web Search Reference snippets and device driver details in the System Context to supply correct, realistic specifications.
6. **Offline search status**: If the Web Search Reference indicates that the system is Offline (unable to connect online), you must report back to the user stating that you cannot fetch specifications from online right now.
"""
        try:
            with open(GUARDRAILS_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            import sys
            print(f"Error creating default Guardrails.md: {e}", file=sys.stderr)

def ensure_directories():
    """Ensures reports, logs, comparisons folders, and guardrails exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    COMPARISONS_DIR.mkdir(parents=True, exist_ok=True)
    ensure_guardrails_file()

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
