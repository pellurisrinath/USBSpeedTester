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
        self.root.geometry("540x400")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # Main app path setup
        self.install_dir = Path("C:\\ProgramData\\USBSpeedTest")
        self.dest_exe = self.install_dir / "USBSpeedTest.exe"
        
        # Initialize logging
        self.log_verbose("=== USB Speed Test & Monitor Setup Started ===")
        self.log_verbose(f"System Platform: {sys.platform}")
        self.log_verbose(f"Python Version: {sys.version}")
        self.log_verbose(f"Executable Mode (sys.frozen): {getattr(sys, 'frozen', False)}")
        
        # Determine source exe path (bundled via PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            self.source_exe = Path(sys._MEIPASS) / "USBSpeedTest.exe"
            self.log_verbose(f"PyInstaller temporary extraction folder (_MEIPASS): {sys._MEIPASS}")
        else:
            self.source_exe = Path(__file__).parent.parent / "dist" / "USBSpeedTest.exe"
            
        self.log_verbose(f"Source Executable path resolved to: {self.source_exe}")
        self.log_verbose(f"Destination Executable path resolved to: {self.dest_exe}")

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
        # Header banner (packed at the top)
        header_frame = tk.Frame(self.root, bg=COLOR_PANEL, height=80)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = ttk.Label(header_frame, text="USB Speed Test & Monitor", style="Title.TLabel", background=COLOR_PANEL)
        title_label.pack(anchor=tk.W, padx=20, pady=(15, 2))

        subtitle_label = ttk.Label(header_frame, text="Setup Wizard - Standalone Installer", style="Subtitle.TLabel", background=COLOR_PANEL)
        subtitle_label.pack(anchor=tk.W, padx=20)

        # Bottom buttons panel (packed at the bottom to ensure visibility and prevent clipping)
        btn_frame = tk.Frame(self.root, bg=COLOR_BG, height=60)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame.pack_propagate(False)

        # Divider line above buttons (packed just above the buttons)
        divider = tk.Frame(self.root, bg=COLOR_PANEL, height=1)
        divider.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_cancel = tk.Button(
            btn_frame, 
            text="Cancel", 
            command=self.root.quit,
            bg="#334155",            # High-visibility Slate 700 background
            fg="#FFFFFF",            # High-contrast white text
            activebackground="#475569", 
            activeforeground="#FFFFFF",
            bd=1, 
            relief=tk.FLAT,
            padx=18, 
            pady=6, 
            font=("Segoe UI", 9, "bold")
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=(10, 20), pady=12)

        self.btn_install = tk.Button(
            btn_frame, 
            text="Install Now", 
            command=self.start_installation,
            bg=COLOR_PRIMARY,        # Vibrant Purple background
            fg="#FFFFFF",            # High-contrast white text
            activebackground="#7C3AED", 
            activeforeground="#FFFFFF",
            bd=1, 
            relief=tk.FLAT,
            padx=22, 
            pady=6, 
            font=("Segoe UI", 9, "bold")
        )
        self.btn_install.pack(side=tk.RIGHT, pady=12)

        # Body area (packed in the center, filling remaining space)
        body_frame = tk.Frame(self.root, bg=COLOR_BG)
        body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=15)

        desc_text = (
            "This installer will deploy the USB Speed Test & Monitor application to your computer.\n\n"
            "• Standalone binary (no Python installation or setup required)\n"
            "• Installs directly to local path:\n"
            "  C:\\ProgramData\\USBSpeedTest\n"
            "• Configures system tray helper, notifications, and shortcuts."
        )
        self.desc_label = ttk.Label(body_frame, text=desc_text, justify=tk.LEFT)
        self.desc_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        # Progress / Status display
        self.status_label = ttk.Label(body_frame, text="Ready to install.", style="Status.TLabel")
        self.status_label.pack(anchor=tk.W, pady=(5, 2))

        self.progress = ttk.Progressbar(body_frame, mode='determinate', style="TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 10))
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

    def log_verbose(self, message):
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            log_path = self.install_dir / "setup_install.log"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
            print(f"[{timestamp}] {message}")
        except Exception as e:
            sys.stderr.write(f"Failed to log message: {e}\n")

    def start_installation(self):
        # Disable buttons
        self.btn_install.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.DISABLED)
        self.launch_check.config(state=tk.DISABLED)
        
        self.log_verbose("User triggered start_installation(). Launching installation thread...")
        # Start install thread
        threading.Thread(target=self.install_process, daemon=True).start()

    def create_shortcut(self, target, shortcut_path, description="USB Speed Test & Monitor"):
        self.log_verbose(f"Creating shortcut: '{shortcut_path}' pointing to '{target}'...")
        try:
            ps_command = (
                f'$WshShell = New-Object -ComObject WScript.Shell; '
                f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
                f'$Shortcut.TargetPath = "{target}"; '
                f'$Shortcut.Description = "{description}"; '
                f'$Shortcut.WorkingDirectory = "{os.path.dirname(target)}"; '
                f'$Shortcut.IconLocation = "{target}, 0"; '
                f'$Shortcut.Save()'
            )
            self.log_verbose(f"Executing PowerShell command: {ps_command}")
            res = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, check=True)
            if res.stdout:
                self.log_verbose(f"PowerShell stdout: {res.stdout.strip()}")
            if res.stderr:
                self.log_verbose(f"PowerShell stderr: {res.stderr.strip()}")
            self.log_verbose(f"Shortcut created successfully at: '{shortcut_path}'")
            return True
        except Exception as e:
            import traceback
            self.log_verbose(f"Failed to create shortcut at '{shortcut_path}': {e}\n{traceback.format_exc()}")
            return False

    def install_process(self):
        self.log_verbose("--- Starting installation process thread ---")
        try:
            # 1. Check if source executable exists
            self.update_status("Locating installer payload...", 10)
            self.log_verbose(f"Checking if source payload exists at '{self.source_exe}'...")
            time.sleep(0.5)
            
            if not os.path.exists(self.source_exe):
                raise FileNotFoundError(
                    f"Installer payload not found at {self.source_exe}.\n"
                    "Please build the main executable first."
                )
            
            payload_size = os.path.getsize(self.source_exe)
            self.log_verbose(f"Installer payload located. Size: {payload_size} bytes.")

            # 2. Check if destination exe is locked/running
            self.update_status("Checking for running instances...", 20)
            self.log_verbose(f"Checking if destination file '{self.dest_exe}' is write-accessible/locked...")
            if self.dest_exe.exists():
                try:
                    # Attempt to open for writing in append mode to check if locked
                    with open(self.dest_exe, 'ab') as f:
                        pass
                    self.log_verbose("Destination file is not locked.")
                except IOError as ioe:
                    self.log_verbose(f"Destination file locked: {ioe}. Prompting user to close app.")
                    self.update_status("Waiting for application to close...", 30)
                    response = messagebox.askretrycancel(
                        "File Lock Detected",
                        "The application (USBSpeedTest.exe) is currently running.\n"
                        "Please close the application or exit it from the system tray, then click Retry."
                    )
                    if not response:
                        self.log_verbose("User chose to cancel installation on file lock prompt.")
                        raise Exception("Installation cancelled: Application is running and cannot be overwritten.")
                    
                    # Double check
                    try:
                        with open(self.dest_exe, 'ab') as f:
                            pass
                        self.log_verbose("Destination file unlocked after user closed the app.")
                    except IOError as ioe2:
                        self.log_verbose(f"Destination file is still locked after user retry: {ioe2}")
                        raise Exception("Installation failed: Target executable is still locked. Please close it.")

            # 3. Create target directory
            self.update_status("Creating installation folder...", 40)
            self.log_verbose(f"Ensuring installation directory exists: '{self.install_dir}'...")
            self.install_dir.mkdir(parents=True, exist_ok=True)
            time.sleep(0.3)

            # 4. Copy executable
            self.update_status("Deploying files (USBSpeedTest.exe)...", 60)
            self.log_verbose(f"Copying source '{self.source_exe}' to destination '{self.dest_exe}'...")
            shutil.copy2(self.source_exe, self.dest_exe)
            dest_size = os.path.getsize(self.dest_exe)
            self.log_verbose(f"Copy completed successfully. Destination file size: {dest_size} bytes.")
            time.sleep(0.5)

            # 5. Create Shortcuts
            self.update_status("Creating shortcuts...", 80)
            userprofile = os.environ.get("USERPROFILE")
            appdata = os.environ.get("APPDATA")
            programdata = os.environ.get("ProgramData", "C:\\ProgramData")
            self.log_verbose(f"Shortcut environment: USERPROFILE='{userprofile}', APPDATA='{appdata}', ProgramData='{programdata}'")
            
            shortcuts_created = 0

            # 5a. Desktop shortcut (current user)
            if userprofile:
                desktop_lnk = os.path.join(userprofile, "Desktop", "USB Speed Test & Monitor.lnk")
                if self.create_shortcut(str(self.dest_exe), desktop_lnk):
                    shortcuts_created += 1

            # 5b. Current-user Start Menu — dedicated subfolder under Programs
            if appdata:
                user_sm_folder = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "USB Speed Test & Monitor"
                self.log_verbose(f"Creating user Start Menu folder: '{user_sm_folder}'...")
                user_sm_folder.mkdir(parents=True, exist_ok=True)
                user_sm_lnk = user_sm_folder / "USB Speed Test & Monitor.lnk"
                if self.create_shortcut(str(self.dest_exe), str(user_sm_lnk)):
                    shortcuts_created += 1

            # 5c. All-Users Start Menu (ProgramData) — visible to every Windows account
            all_users_sm_folder = Path(programdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "USB Speed Test & Monitor"
            self.log_verbose(f"Creating All Users Start Menu folder: '{all_users_sm_folder}'...")
            try:
                all_users_sm_folder.mkdir(parents=True, exist_ok=True)
                all_users_sm_lnk = all_users_sm_folder / "USB Speed Test & Monitor.lnk"
                if self.create_shortcut(str(self.dest_exe), str(all_users_sm_lnk)):
                    shortcuts_created += 1
            except PermissionError:
                self.log_verbose("Skipped All-Users Start Menu shortcut: insufficient permissions (not running as Administrator).")
                    
            self.log_verbose(f"Shortcuts creation complete. Total created: {shortcuts_created}")
            time.sleep(0.3)

            # 6. Complete
            self.update_status("Installation completed successfully!", 100, COLOR_SUCCESS)
            self.log_verbose("--- Installation completed successfully ---")
            
            # Switch buttons
            self.btn_cancel.config(text="Close", state=tk.NORMAL)
            self.btn_cancel.config(command=self.root.quit)
            self.btn_install.pack_forget() # Remove install button

            # Launch application if requested
            if self.launch_var.get():
                self.update_status("Launching application...", 100, COLOR_SUCCESS)
                self.log_verbose(f"Launching installed application in detached process: '{self.dest_exe}'...")
                proc = subprocess.Popen([str(self.dest_exe)], creationflags=subprocess.DETACHED_PROCESS)
                self.log_verbose(f"Detached process started. Process ID: {proc.pid}. Setup installer exiting.")
                time.sleep(0.5)
                self.root.quit()

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            self.log_verbose(f"CRITICAL ERROR: Installation failed: {e}\n{error_trace}")
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
