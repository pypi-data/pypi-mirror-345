"""
Python Script Launcher

Lets the user choose between different python versions, and launches either the regular python script in the chosen version or a streamlit application, shown in the launcher icons.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import platform
import json

SETTINGS_FILE = "launcher_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"custom_paths": []}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def find_python_executables():
    paths = []
    system = platform.system()

    if system == "Windows":
        try:
            for name in os.listdir("C:/"):
                full_path = os.path.join("C:/", name, "python.exe")
                if os.path.exists(full_path):
                    paths.append(full_path)
        except Exception as e:
            print(f"Skipping C:/ scan: {e}")

        try:
            local_appdata = os.environ.get("LOCALAPPDATA")
            if local_appdata:
                py_dir = os.path.join(local_appdata, "Programs", "Python")
                if os.path.exists(py_dir):
                    for name in os.listdir(py_dir):
                        full_path = os.path.join(py_dir, name, "python.exe")
                        if os.path.exists(full_path):
                            paths.append(full_path)
        except Exception as e:
            print(f"Skipping LOCALAPPDATA scan: {e}")

    elif system == "Linux":
        for dir_path in ["/usr/bin", "/usr/local/bin"]:
            try:
                if os.path.exists(dir_path):
                    for name in os.listdir(dir_path):
                        if name.startswith("python") and os.access(os.path.join(dir_path, name), os.X_OK):
                            paths.append(os.path.join(dir_path, name))
            except Exception as e:
                print(f"Skipping Linux path {dir_path}: {e}")

    else:
        print(f"No known Python install paths defined for OS: {system}")

    return paths

def get_script_type(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "streamlit" in content:
                return "Streamlit"
            elif "def " in content or "import " in content:
                return "Python"
    except:
        pass
    return "Unknown"

def get_script_description(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith("##"):
                return first_line[2:].strip()
    except:
        pass
    return None

def run_script(python_exec, script, script_type):
    if script_type == "Streamlit":
        cmd = f'"{python_exec}" -m streamlit run "{script}"'
    elif script_type == "Python":
        cmd = f'"{python_exec}" "{script}"'
    else:
        messagebox.showerror("Error", "Unknown script type")
        return
    subprocess.Popen(cmd, shell=True)

class PythonLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Script Launcher")
        self.settings = load_settings()

        self.python_versions = []
        self.selected_python = tk.StringVar()
        self.custom_python = tk.StringVar()

        self.setup_ui()
        self.refresh_python_list()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # OS Info Label
        current_os = platform.system()
        ttk.Label(frame, text=f"Running on: {current_os}", foreground="gray").pack(anchor="w", pady=(0, 10))

        # Python Version Selector
        ttk.Label(frame, text="Python Version:").pack(anchor="w")
        self.python_combo = ttk.Combobox(frame, textvariable=self.selected_python, state="readonly", width=80)
        self.python_combo.pack(fill="x", pady=(0, 5))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_frame, text="Rescan", command=self.refresh_python_list).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add Python Path...", command=self.browse_python_path).pack(side="left", padx=5)

        # Script list label
        ttk.Label(frame, text="Python Scripts:").pack(anchor="w", pady=(10, 0))

        # Script list frame
        self.script_frame = ttk.Frame(frame)
        self.script_frame.pack(fill="both", expand=True)

        self.populate_scripts()

    def refresh_python_list(self):
        self.python_versions = find_python_executables()
        self.python_versions += self.settings.get("custom_paths", [])
        self.python_versions = sorted(set(self.python_versions))
        self.python_combo["values"] = self.python_versions
        if self.python_versions:
            self.selected_python.set(self.python_versions[0])

    def browse_python_path(self):
        path = filedialog.askopenfilename(title="Select python.exe or python binary")
        if path and os.path.isfile(path):
            self.settings["custom_paths"].append(path)
            self.refresh_python_list()
            save_settings(self.settings)

    def populate_scripts(self):
        for widget in self.script_frame.winfo_children():
            widget.destroy()

        scripts = [f for f in os.listdir() if f.endswith(".py") and f != os.path.basename(__file__)]
        if not scripts:
            ttk.Label(self.script_frame, text="No Python scripts found.").pack()
            return

        for script in scripts:
            script_type = get_script_type(script)
            script_desc = get_script_description(script)

            container = ttk.Frame(self.script_frame)
            container.pack(fill="x", pady=4)

            # Launch Button
            btn = ttk.Button(container, text=f"{script_type}: {script}",
                             command=lambda s=script, t=script_type: self.launch_script(s, t))
            btn.pack(fill="x")

            # Optional description
            if script_desc:
                desc_label = ttk.Label(container, text=f"  ↳ {script_desc}", foreground="gray", font=("Segoe UI", 9))
                desc_label.pack(anchor="w", padx=10)

    def launch_script(self, script, script_type):
        python_exec = self.selected_python.get()
        if not os.path.exists(python_exec):
            messagebox.showerror("Error", "Selected Python executable not found.")
            return
        run_script(python_exec, script, script_type)

def main():
    import tkinter as tk
    root = tk.Tk()
    app = PythonLauncherApp(root)
    root.mainloop()    

if __name__ == "__main__":
    main()
