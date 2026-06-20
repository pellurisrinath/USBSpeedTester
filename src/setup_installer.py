import os
import sys
import shutil
import subprocess
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Theme colors matching USB Speed Test & Monitor App
COLOR_BG = "#0F172A"       # Slate 900
COLOR_PANEL = "#1E293B"    # Slate 800
COLOR_TEXT = "#F8FAFC"     # Slate 50
COLOR_MUTED = "#94A3B8"    # Slate 400
COLOR_PRIMARY = "#8B5CF6"  # Purple 500 (Primary)
COLOR_SUCCESS = "#10B981"  # Emerald 500

class SetupInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Speed Test & Monitor Setup")
        self.root.geometry("520x360")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # Main app path setup
        self.install_dir = Path("C:\\ProgramData\\USBSpeedTest")
        self.dest_exe = self.install_dir / "USBSpeedTest.exe"
        
        # Determine source exe path (bundled via PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            self.source_exe = Path(sys._MEIPASS) / "USBSpeedTest.exe"
        else:
            self.source_exe = Path(__file__).parent.parent / "dist" / "USBSpeedTest.exe"

        # Apply styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT)
        self.style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_PRIMARY)
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 9), foreground=COLOR_MUTED)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "italic"), foreground=COLOR_PRIMARY)
        
        self.style.configure("TProgressbar", thickness=15, troughcolor=COLOR_PANEL, background=COLOR_PRIMARY)
        
        # Build UI layout
        self.create_widgets()

    def create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg=COLOR_PANEL, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = ttk.Label(header_frame, text="USB Speed Test & Monitor", style="Title.TLabel", background=COLOR_PANEL)
        title_label.pack(anchor=tk.W, padx=20, pady=(15, 2))

        subtitle_label = ttk.Label(header_frame, text="Setup Wizard - Standalone Installer", style="Subtitle.TLabel", background=COLOR_PANEL)
        subtitle_label.pack(anchor=tk.W, padx=20)

        # Body area
        body_frame = tk.Frame(self.root, bg=COLOR_BG)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        desc_text = (
            "This installer will deploy the USB Speed Test & Monitor application to your computer.\n\n"
            "• Standalone binary (no Python installation or setup required)\n"
            "• Installs directly to local path:\n"
            "  C:\\ProgramData\\USBSpeedTest\n"
            "• Configures system tray helper, notifications, and shortcuts."
        )
        self.desc_label = ttk.Label(body_frame, text=desc_text, justify=tk.LEFT)
        self.desc_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 20))

        # Progress / Status display
        self.status_label = ttk.Label(body_frame, text="Ready to install.", style="Status.TLabel")
        self.status_label.pack(anchor=tk.W, pady=(5, 5))

        self.progress = ttk.Progressbar(body_frame, mode='determinate', style="TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress['value'] = 0

        # Launch checkbox
        self.launch_var = tk.BooleanVar(value=True)
        self.launch_check = tk.Checkbutton(
            body_frame, 
            text="Launch application after installation finishes", 
            variable=self.launch_var,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            activebackground=COLOR_BG,
            activeforeground=COLOR_TEXT,
            selectcolor=COLOR_PANEL,
            font=("Segoe UI", 9)
        )
        self.launch_check.pack(anchor=tk.W)

        # Divider line above buttons
        divider = tk.Frame(self.root, bg=COLOR_PANEL, height=1)
        divider.pack(fill=tk.X)

        # Bottom buttons panel
        btn_frame = tk.Frame(self.root, bg=COLOR_BG, height=50)
        btn_frame.pack(fill=tk.X)
        btn_frame.pack_propagate(False)

        self.btn_cancel = tk.Button(
            btn_frame, 
            text="Cancel", 
            command=self.root.quit,
            bg=COLOR_PANEL, 
            fg=COLOR_TEXT, 
            activebackground=COLOR_BG, 
            activeforeground=COLOR_TEXT,
            bd=0, 
            padx=15, 
            pady=5, 
            font=("Segoe UI", 9)
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=(10, 20), pady=10)

        self.btn_install = tk.Button(
            btn_frame, 
            text="Install Now", 
            command=self.start_installation,
            bg=COLOR_PRIMARY, 
            fg=COLOR_TEXT, 
            activebackground="#7C3AED", 
            activeforeground=COLOR_TEXT,
            bd=0, 
            padx=20, 
            pady=5, 
            font=("Segoe UI", 9, "bold")
        )
        self.btn_install.pack(side=tk.RIGHT, pady=10)

    def start_installation(self):
        # Disable buttons
        self.btn_install.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.DISABLED)
        self.launch_check.config(state=tk.DISABLED)
        
        # Start install thread
        threading.Thread(target=self.install_process, daemon=True).start()

    def create_shortcut(self, target, shortcut_path, description="USB Speed Test & Monitor"):
        try:
            ps_command = (
                f'$WshShell = New-Object -ComObject WScript.Shell; '
                f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
                f'$Shortcut.TargetPath = "{target}"; '
                f'$Shortcut.Description = "{description}"; '
                f'$Shortcut.WorkingDirectory = "{os.path.dirname(target)}"; '
                f'$Shortcut.Save()'
            )
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False

    def install_process(self):
        try:
            # 1. Check if source executable exists
            self.update_status("Locating installer payload...", 10)
            time.sleep(0.5)
            
            if not os.path.exists(self.source_exe):
                raise FileNotFoundError(
                    f"Installer payload not found at {self.source_exe}.\n"
                    "Please build the main executable first."
                )

            # 2. Check if destination exe is locked/running
            self.update_status("Checking for running instances...", 20)
            if self.dest_exe.exists():
                try:
                    # Attempt to open for writing in append mode to check if locked
                    with open(self.dest_exe, 'ab') as f:
                        pass
                except IOError:
                    self.update_status("Waiting for application to close...", 30)
                    response = messagebox.askretrycancel(
                        "File Lock Detected",
                        "The application (USBSpeedTest.exe) is currently running.\n"
                        "Please close the application or exit it from the system tray, then click Retry."
                    )
                    if not response:
                        raise Exception("Installation cancelled: Application is running and cannot be overwritten.")
                    
                    # Double check
                    try:
                        with open(self.dest_exe, 'ab') as f:
                            pass
                    except IOError:
                        raise Exception("Installation failed: Target executable is still locked. Please close it.")

            # 3. Create target directory
            self.update_status("Creating installation folder...", 40)
            self.install_dir.mkdir(parents=True, exist_ok=True)
            time.sleep(0.3)

            # 4. Copy executable
            self.update_status("Deploying files (USBSpeedTest.exe)...", 60)
            shutil.copy2(self.source_exe, self.dest_exe)
            time.sleep(0.5)

            # 5. Create Shortcuts
            self.update_status("Creating shortcuts...", 80)
            userprofile = os.environ.get("USERPROFILE")
            appdata = os.environ.get("APPDATA")
            
            shortcuts_created = 0
            if userprofile:
                desktop_lnk = os.path.join(userprofile, "Desktop", "USB Speed Test & Monitor.lnk")
                if self.create_shortcut(str(self.dest_exe), desktop_lnk):
                    shortcuts_created += 1
            
            if appdata:
                startmenu_folder = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                startmenu_folder.mkdir(parents=True, exist_ok=True)
                startmenu_lnk = startmenu_folder / "USB Speed Test & Monitor.lnk"
                if self.create_shortcut(str(self.dest_exe), str(startmenu_lnk)):
                    shortcuts_created += 1
            time.sleep(0.3)

            # 6. Complete
            self.update_status("Installation completed successfully!", 100, COLOR_SUCCESS)
            
            # Switch buttons
            self.btn_cancel.config(text="Close", state=tk.NORMAL)
            self.btn_cancel.config(command=self.root.quit)
            self.btn_install.pack_forget() # Remove install button

            # Launch application if requested
            if self.launch_var.get():
                self.update_status("Launching application...", 100, COLOR_SUCCESS)
                subprocess.Popen([str(self.dest_exe)], creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
                time.sleep(0.5)
                self.root.quit()

        except Exception as e:
            self.update_status("Error during installation.", 100, "#EF4444")
            messagebox.showerror("Installation Failed", str(e))
            self.btn_install.config(state=tk.NORMAL)
            self.btn_cancel.config(state=tk.NORMAL)
            self.launch_check.config(state=tk.NORMAL)

    def update_status(self, text, percent, color=COLOR_PRIMARY):
        self.root.after(0, self._update_status_ui, text, percent, color)

    def _update_status_ui(self, text, percent, color):
        self.status_label.config(text=text)
        self.style.configure("Status.TLabel", foreground=color)
        self.progress['value'] = percent

if __name__ == "__main__":
    # Standard Tkinter boilerplate
    root = tk.Tk()
    
    # Simple icon fallback or purple icon
    try:
        # If there's an icon in the directory we could set it, but default title bar is fine.
        pass
    except:
        pass
        
    app = SetupInstaller(root)
    root.mainloop()
