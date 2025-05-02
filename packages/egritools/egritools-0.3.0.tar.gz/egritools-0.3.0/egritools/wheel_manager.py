"""
Offline Python Wheel Manager

This tool allows you to parse pip commands, download and install wheels locally,
generate requirements.txt, and restore environments offline.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
import os
import threading
import re

CONFIG_FILE = "wheeldl_config.json"

class WheelDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Wheel Manager")

        self.packages_var = tk.StringVar()
        self.index_url_var = tk.StringVar(value="https://download.pytorch.org/whl/cu118")
        self.save_path_var = tk.StringVar()
        self.pip_command_var = tk.StringVar()
        self.local_install_var = tk.StringVar()

        self.suggestions = []
        self.suggestion_box = None
        self.local_entry = None

        self.ensure_config_exists()
        self.load_config()
        self.build_gui()

    def ensure_config_exists(self):
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "packages": "",
                "index_url": "https://download.pytorch.org/whl/cu118",
                "save_path": ""
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.packages_var.set(data.get("packages", ""))
                self.index_url_var.set(data.get("index_url", ""))
                self.save_path_var.set(data.get("save_path", ""))

    def save_config(self):
        data = {
            "packages": self.packages_var.get(),
            "index_url": self.index_url_var.get(),
            "save_path": self.save_path_var.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Saved", "Configuration saved.")

    def build_gui(self):
        instructions = (
            "\U0001F4A1 How to use:\n"
            "- Paste a pip command OR type package names manually.\n"
            "- Set optional index URL.\n"
            "- Choose where to save wheels.\n"
            "- Click 'Download Wheels' to cache .whl files.\n"
            "- Click 'Install from Saved Wheels' to install offline.\n"
        )
        tk.Label(self.root, text=instructions, justify="left", fg="gray").pack(pady=(5, 0))

        tk.Label(self.root, text="Paste pip command (optional):").pack()
        tk.Entry(self.root, textvariable=self.pip_command_var, width=80).pack()
        tk.Button(self.root, text="Parse pip command", command=self.parse_pip_command).pack(pady=(0, 10))

        tk.Label(self.root, text="Packages (space-separated):").pack()
        tk.Entry(self.root, textvariable=self.packages_var, width=60).pack()
        tk.Button(self.root, text="Clear Packages", command=lambda: self.packages_var.set(""))\
.pack(pady=(0, 10))

        tk.Label(self.root, text="Index URL (optional):").pack()
        tk.Entry(self.root, textvariable=self.index_url_var, width=60).pack()
        tk.Button(self.root, text="Clear Index URL", command=lambda: self.index_url_var.set(""))\
.pack(pady=(0, 10))

        tk.Label(self.root, text="Save/Load Directory:").pack()
        tk.Entry(self.root, textvariable=self.save_path_var, width=60).pack()
        tk.Button(self.root, text="Browse Folder", command=self.browse_folder).pack()

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(pady=(10, 5))

        tk.Button(self.root, text="Download Wheels", command=self.threaded_download).pack(pady=5)
        tk.Button(self.root, text="Install from Saved Wheels (above packages)", command=self.threaded_install).pack(pady=5)

        tk.Label(self.root, text="Install from Saved Wheels (enter like pip):").pack()
        self.local_entry = tk.Entry(self.root, textvariable=self.local_install_var, width=60)
        self.local_entry.pack()
        self.local_entry.bind("<KeyRelease>", self.update_suggestions)
        self.local_entry.bind("<FocusOut>", lambda e: self.hide_suggestions())
        tk.Button(self.root, text="Install These from Saved Wheels", command=self.threaded_custom_local_install).pack(pady=(5, 10))
        tk.Button(self.root, text="Install from requirements.txt (local wheels)", command=self.threaded_requirements_install).pack(pady=5)


        tk.Button(self.root, text="View Installed Packages", command=self.show_installed_packages).pack(pady=(0, 5))
        tk.Button(self.root, text="View Saved Wheel Packages", command=self.show_available_wheels).pack(pady=(0, 10))
        tk.Button(self.root, text="Save Installed Packages as requirements.txt", command=self.save_installed_packages).pack(pady=(0, 10))
        tk.Button(self.root, text="Save Config", command=self.save_config).pack(pady=5)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_var.set(path)

    def parse_pip_command(self):
        cmd = self.pip_command_var.get().strip()
        if not cmd.lower().startswith("pip install"):
            messagebox.showerror("Invalid", "Command must start with 'pip install'")
            return

        parts = cmd.split()
        packages = []
        index_url = ""
        skip_next = False
        for i, part in enumerate(parts[2:]):
            if skip_next:
                skip_next = False
                continue
            if part in ("--index-url", "-i") and i + 3 < len(parts):
                index_url = parts[2 + i + 1]
                skip_next = True
            elif part.startswith("--"):
                continue
            else:
                packages.append(part)

        self.packages_var.set(" ".join(packages))
        if index_url:
            self.index_url_var.set(index_url)
        messagebox.showinfo("Parsed", "Pip command parsed successfully.")

    def threaded_download(self):
        threading.Thread(target=self.download_wheels, daemon=True).start()

    def threaded_install(self):
        threading.Thread(target=self.install_wheels, daemon=True).start()

    def threaded_custom_local_install(self):
        threading.Thread(target=self.local_install_from_saved, daemon=True).start()

    def run_command(self, cmd):
        try:
            self.progress_bar.start()
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command failed:\n{e}")
        finally:
            self.progress_bar.stop()

    def download_wheels(self):
        packages = self.packages_var.get().strip()
        save_path = self.save_path_var.get()
        index_url = self.index_url_var.get().strip()

        if not packages or not save_path:
            messagebox.showwarning("Missing Info", "Please enter packages and select a save folder.")
            return

        os.makedirs(save_path, exist_ok=True)
        cmd = f'pip download {packages} -d "{save_path}"'
        if index_url:
            cmd += f' --index-url {index_url}'

        self.run_command(cmd)
        messagebox.showinfo("Done", "Download complete.")

    def install_wheels(self):
        save_path = self.save_path_var.get()
        packages = self.packages_var.get().strip()
        if not save_path or not packages:
            messagebox.showwarning("Missing Info", "Please provide package names and save folder.")
            return

        cmd = f'pip install --no-index --find-links "{save_path}" {packages}'
        self.run_command(cmd)
        messagebox.showinfo("Done", "Install complete.")

    def local_install_from_saved(self):
        save_path = self.save_path_var.get()
        local_packages = self.local_install_var.get().strip()
        if not save_path or not local_packages:
            messagebox.showwarning("Missing Info", "Please enter packages and select a save folder.")
            return

        cmd = f'pip install --no-index --find-links "{save_path}" {local_packages}'
        self.run_command(cmd)
        messagebox.showinfo("Done", "Install complete.")

    def show_installed_packages(self):
        try:
            output = subprocess.check_output("pip list", shell=True, text=True)
            popup = tk.Toplevel(self.root)
            popup.title("Installed Packages")
            text_widget = tk.Text(popup, wrap="none", width=80, height=25)
            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")
            text_widget.pack()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Could not retrieve installed packages:\n{e}")

    def show_available_wheels(self):
        wheel_dir = self.save_path_var.get().strip()
        if not wheel_dir or not os.path.isdir(wheel_dir):
            messagebox.showwarning("Missing Folder", "Please select a valid folder containing saved .whl files.")
            return

        wheels = [f for f in os.listdir(wheel_dir) if f.endswith(".whl")]
        if not wheels:
            messagebox.showinfo("No Wheels", "No .whl files found in the selected folder.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Saved Wheel Files (Available for Install)")
        text_widget = tk.Text(popup, wrap="none", width=80, height=25)
        text_widget.insert("1.0", "\U0001F4E6 Available Offline Packages:\n\n")

        for wheel in wheels:
            match = re.match(r"^([A-Za-z0-9_.\-]+)-([0-9][\w\.]*)", wheel)
            if match:
                pkg, ver = match.groups()
                text_widget.insert(tk.END, f"{pkg}=={ver}\n")
            else:
                text_widget.insert(tk.END, f"{wheel}\n")

        text_widget.config(state="disabled")
        text_widget.pack()

    def update_suggestions(self, event=None):
        self.hide_suggestions()
        parts = self.local_install_var.get().strip().split()
        if not parts:
            return
        current_input = parts[-1].lower()

        wheel_dir = self.save_path_var.get().strip()
        if not wheel_dir or not os.path.isdir(wheel_dir):
            return

        wheels = [f for f in os.listdir(wheel_dir) if f.endswith(".whl")]
        suggestions = set()
        for wheel in wheels:
            match = re.match(r"^([A-Za-z0-9_.\-]+)-", wheel)
            if match:
                pkg = match.group(1).lower()
                if pkg.startswith(current_input):
                    suggestions.add(pkg)

        if suggestions:
            self.suggestion_box = tk.Listbox(self.root, height=min(5, len(suggestions)))
            for suggestion in sorted(suggestions):
                self.suggestion_box.insert(tk.END, suggestion)

            self.suggestion_box.bind("<Button-1>", self.insert_suggestion)

            if self.local_entry:
                x = self.local_entry.winfo_rootx() - self.root.winfo_rootx()
                y = self.local_entry.winfo_rooty() - self.root.winfo_rooty() + self.local_entry.winfo_height()
                self.suggestion_box.place(x=x, y=y)

    def insert_suggestion(self, event):
        selected = self.suggestion_box.get(tk.ACTIVE)
        current_text = self.local_install_var.get()
        parts = current_text.strip().split()
        if parts:
            parts[-1] = selected
        else:
            parts = [selected]
        self.local_install_var.set(" ".join(parts))
        self.hide_suggestions()

    def hide_suggestions(self):
        if self.suggestion_box:
            self.suggestion_box.destroy()
            self.suggestion_box = None

    def save_installed_packages(self):
        try:
            packages = subprocess.check_output("pip freeze", shell=True, text=True)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                initialfile="requirements.txt",
                title="Save requirements.txt"
            )
            if save_path:
                with open(save_path, "w") as f:
                    f.write(packages)
                messagebox.showinfo("Saved", f"Installed packages saved to {save_path}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to get installed packages:\n{e}")

    def threaded_requirements_install(self):
        threading.Thread(target=self.install_from_requirements_file, daemon=True).start()

    def install_from_requirements_file(self):
        req_path = filedialog.askopenfilename(
            filetypes=[("Requirements Files", "*.txt")],
            title="Select requirements.txt"
        )
        if not req_path:
            return

        save_path = self.save_path_var.get().strip()
        if not save_path or not os.path.isdir(save_path):
            messagebox.showwarning("Missing Folder", "Please select a valid save folder first.")
            return

        # Read requirements
        try:
            with open(req_path, "r") as f:
                required_packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read requirements.txt:\n{e}")
            return

        # Extract names and versions from wheel files
        existing_wheels = [f for f in os.listdir(save_path) if f.endswith(".whl")]
        existing = set()
        for wheel in existing_wheels:
            match = re.match(r"^([A-Za-z0-9_.\-]+)-([0-9][\w\.]*)", wheel)
            if match:
                pkg, ver = match.groups()
                existing.add(f"{pkg.replace('_', '-')}=={ver}")

        missing = [pkg for pkg in required_packages if pkg not in existing]

        if missing:
            if messagebox.askyesno("Download missing?", f"{len(missing)} package(s) are missing. Download now?"):
                cmd = f'pip download {" ".join(missing)} -d "{save_path}"'
                self.run_command(cmd)
            else:
                messagebox.showinfo("Cancelled", "Installation aborted due to missing packages.")
                return

        # Install all from local
        cmd = f'pip install --no-index --find-links "{save_path}" -r "{req_path}"'
        self.run_command(cmd)
        messagebox.showinfo("Done", "Installation complete from requirements.txt")

def main():
    import tkinter as tk
    root = tk.Tk()
    app = WheelDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

