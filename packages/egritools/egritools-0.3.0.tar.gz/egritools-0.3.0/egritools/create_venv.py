"""
Python Virual Environment Creator

Checks for eg c:/python310 installations and lets the user create a custom python venv with a start.bat for easy use.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess

def find_python_versions():
    python_paths = []
    root_dirs = [os.path.join("C:/", d) for d in os.listdir("C:/") if os.path.isdir(os.path.join("C:/", d))]

    for dir_path in root_dirs:
        possible_path = os.path.join(dir_path, "python.exe")
        if os.path.exists(possible_path):
            python_paths.append(possible_path)
    
    return python_paths

def select_target_folder():
    folder = filedialog.askdirectory()
    if folder:
        target_folder.set(folder)

def create_virtual_env():
    python_path = selected_python.get()
    folder = target_folder.get()
    extras = extra_packages.get().strip().split()
    log_text.delete(1.0, tk.END)  # Clear previous logs
    progress["value"] = 0
    root.update_idletasks()

    if not python_path or not folder:
        messagebox.showerror("Error", "Please select both Python version and target folder.")
        return

    try:
        log_text.insert(tk.END, "Creating virtual environment...\n")
        subprocess.run([python_path, "-m", "venv", folder], check=True)
        progress["value"] = 25
        root.update_idletasks()

        bat_path = os.path.join(folder, "start.bat")
        activate_path = os.path.join(folder, "Scripts", "activate")
        with open(bat_path, "w") as f:
            f.write(f'start cmd /k "{activate_path}"')
        log_text.insert(tk.END, f"Virtual environment created.\nStart file: {bat_path}\n")

        # Install requirements.txt
        pip_path = os.path.join(folder, "Scripts", "pip.exe")
        req_path = os.path.join(folder, "requirements.txt")
        req_packages = []

        if os.path.exists(req_path):
            log_text.insert(tk.END, "Found requirements.txt. Installing...\n")
            with open(req_path, "r") as rf:
                req_packages = [line.strip().split("==")[0] for line in rf if line.strip()]
            log_text.insert(tk.END, "Installing requirements individually to avoid halts...\n")
            with open(req_path, "r") as rf:
                for line in rf:
                    pkg = line.strip()
                    if pkg:
                        log_text.insert(tk.END, f"⏳ Installing: {pkg}...\n")
                        result = subprocess.run([pip_path, "install", pkg], capture_output=True, text=True)
                        if result.returncode == 0:
                            log_text.insert(tk.END, f"✅ Installed: {pkg}\n")
                        else:
                            log_text.insert(tk.END, f"❌ Failed: {pkg}\n{result.stderr}\n")

        progress["value"] = 60
        root.update_idletasks()

        # Handle extra packages
        if extras:
            to_install = [pkg for pkg in extras if pkg not in req_packages]
            if to_install:
                log_text.insert(tk.END, f"Installing extra packages: {', '.join(to_install)}\n")
                result = subprocess.run([pip_path, "install"] + to_install, capture_output=True, text=True)
                log_text.insert(tk.END, result.stdout + "\n")
                if result.returncode != 0:
                    log_text.insert(tk.END, "⚠️ Error installing extra packages:\n" + result.stderr + "\n")
            else:
                log_text.insert(tk.END, "All extra packages already included in requirements.txt.\n")

        progress["value"] = 100
        root.update_idletasks()
        log_text.insert(tk.END, "✅ Environment setup complete.\n")

    except subprocess.CalledProcessError as e:
        log_text.insert(tk.END, f"❌ Failed to create virtual environment.\n{e}\n")
        messagebox.showerror("Error", str(e))

def start_search():
    python_listbox['values'] = ["Searching..."]
    root.after(100, update_python_versions)

def update_python_versions():
    python_paths = find_python_versions()
    if not python_paths:
        python_paths = ["No Python versions found."]
    python_listbox['values'] = python_paths
    selected_python.set(python_paths[0] if python_paths else "")

def main():
    global root
    root = tk.Tk()
    root.title("Python Venv Creator")

    global selected_python, target_folder, extra_packages, log_text, progress, python_listbox

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    selected_python = tk.StringVar()
    target_folder = tk.StringVar()

    ttk.Label(frame, text="1. Find Python Versions (like C:/Python310):").pack(anchor="w")
    search_button = ttk.Button(frame, text="Search Python Installations", command=start_search)
    search_button.pack(fill="x")

    ttk.Label(frame, text="2. Select Python Version:").pack(anchor="w", pady=(10, 0))
    python_listbox = ttk.Combobox(frame, textvariable=selected_python, state="readonly", width=80)
    python_listbox.pack(fill="x")

    ttk.Label(frame, text="3. Choose Folder to Install Virtual Env (no subfolder):").pack(anchor="w", pady=(10, 0))
    ttk.Entry(frame, textvariable=target_folder, width=80).pack(fill="x")
    ttk.Button(frame, text="Browse...", command=select_target_folder).pack()

    ttk.Button(frame, text="4. Create Virtual Environment", command=create_virtual_env).pack(pady=(20, 0), fill="x")

    ttk.Label(frame, text="Optional: Additional Packages (space-separated)").pack(anchor="w", pady=(10, 0))
    extra_packages = tk.StringVar()
    ttk.Entry(frame, textvariable=extra_packages, width=80).pack(fill="x")

    ttk.Label(frame, text="Installation Log:").pack(anchor="w", pady=(10, 0))
    log_text = tk.Text(frame, height=10, wrap="word")
    log_text.pack(fill="both", expand=True)

    progress = ttk.Progressbar(frame, orient="horizontal", length=100, mode="determinate")
    progress.pack(fill="x", pady=(10, 0))

    root.mainloop()

if __name__ == "__main__":
    main()

