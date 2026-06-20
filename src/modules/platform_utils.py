import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def get_platform() -> str:
    """Returns the current operating system identifier ('windows', 'darwin', 'linux')."""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'darwin'
    return 'linux'

def open_report_file(path: str) -> bool:
    """Opens report in default system web browser."""
    try:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
        return True
    except Exception as e:
        print(f"Error opening report: {e}", file=sys.stderr)
        try:
            webbrowser.open(f"file:///{path}")
            return True
        except:
            return False

def open_file_explorer(path: str) -> bool:
    """Opens target folder in standard file manager (explorer/finder)."""
    try:
        if sys.platform == 'win32':
            subprocess.run(["explorer", path])
        elif sys.platform == 'darwin':
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
        return True
    except Exception as e:
        print(f"Error opening file explorer: {e}", file=sys.stderr)
        return False
