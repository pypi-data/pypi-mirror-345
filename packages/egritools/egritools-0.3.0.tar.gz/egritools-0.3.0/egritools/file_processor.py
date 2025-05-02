"""
File Processor GUI

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import requests
import os
import json
import threading

# Load lmstudio.py functions directly here
LMSTUDIO_URL = "http://localhost:1234"

def get_models():
    try:
        response = requests.get(f"{LMSTUDIO_URL}/v1/models")
        response.raise_for_status()
        models_data = response.json().get("data", [])
        return [model["id"] for model in models_data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        initial_config = {"prompt1": "", "prompt2": "", "output_dir": "./outputs", "history": []}
        with open("config.json", "w") as f:
            json.dump(initial_config, f, indent=4)
        return initial_config

def save_config(prompt1, prompt2, output_dir):
    config = load_config()
    if "history" not in config:
        config["history"] = []
    config["history"].append({
        "prompt1": config.get("prompt1"),
        "prompt2": config.get("prompt2"),
        "output_dir": config.get("output_dir")
    })
    config.update({"prompt1": prompt1, "prompt2": prompt2, "output_dir": output_dir})
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def process_file_content(content, prompt, server_url, model_id, max_tokens):
    try:
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": f"{prompt}\n{content}"}],
            "max_tokens": max_tokens
        }
        response = requests.post(f"{server_url}/v1/chat/completions", json=payload)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"Error: {e}")
        return ""

def log_failed_file(file_name, error_message, failed_dir):
    os.makedirs(failed_dir, exist_ok=True)
    log_path = os.path.join(failed_dir, "failed_files.log")
    with open(log_path, "a") as log_file:
        log_file.write(f"Failed to process {file_name}: {error_message}\n")

# --- Tkinter App ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Step File Processor (Tkinter Version)")
        
        self.config = load_config()

        # Top Frame
        top_frame = tk.Frame(root)
        top_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(top_frame, text="Server URL:").pack(side="left")
        self.server_entry = tk.Entry(top_frame, width=50)
        self.server_entry.insert(0, "http://localhost:1234")
        self.server_entry.pack(side="left", padx=5)

        tk.Button(top_frame, text="Fetch Models", command=self.refresh_models).pack(side="left", padx=5)

        # Model & Token Frame
        model_frame = tk.Frame(root)
        model_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(model_frame, text="Select Model:").pack(side="left")
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, width=40)
        self.model_dropdown.pack(side="left", padx=5)

        tk.Label(model_frame, text="Max Tokens:").pack(side="left")
        self.max_tokens_entry = tk.Entry(model_frame, width=10)
        self.max_tokens_entry.insert(0, "4096")
        self.max_tokens_entry.pack(side="left", padx=5)

        # Middle Frame
        mid_frame = tk.Frame(root)
        mid_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.uploaded_files = []
        tk.Button(mid_frame, text="Upload Files", command=self.upload_files).pack(pady=5)

        self.files_listbox = tk.Listbox(mid_frame, height=5)
        self.files_listbox.pack(fill="x")

        tk.Button(mid_frame, text="Select Output Directory", command=self.select_output_dir).pack(pady=5)
        self.output_dir_var = tk.StringVar(value=self.config["output_dir"])
        self.output_label = tk.Label(mid_frame, textvariable=self.output_dir_var)
        self.output_label.pack()

        self.include_source_var = tk.BooleanVar(value=True)
        tk.Checkbutton(mid_frame, text="Include Source Data in Second Processing", variable=self.include_source_var).pack(pady=5)

        # Prompt Frame
        prompt_frame = tk.Frame(root)
        prompt_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(prompt_frame, text="First Processing Prompt:").pack()
        self.prompt1_text = tk.Text(prompt_frame, height=5)
        self.prompt1_text.insert("1.0", self.config["prompt1"])
        self.prompt1_text.pack(fill="x")

        tk.Label(prompt_frame, text="Second Processing Prompt:").pack()
        self.prompt2_text = tk.Text(prompt_frame, height=5)
        self.prompt2_text.insert("1.0", self.config["prompt2"])
        self.prompt2_text.pack(fill="x")

        # Load Previous Prompts
        self.history_var = tk.StringVar()
        self.history_dropdown = ttk.Combobox(prompt_frame, textvariable=self.history_var, width=60)
        self.history_dropdown.pack(pady=5)
        self.load_prompt_history()

        tk.Button(prompt_frame, text="Load Selected History", command=self.load_selected_prompt).pack()

        # Process Frame
        process_frame = tk.Frame(root)
        process_frame.pack(padx=10, pady=10)

        tk.Button(process_frame, text="Process First File", command=self.process_first_file).pack(side="left", padx=5)
        tk.Button(process_frame, text="Process and Save All", command=self.process_all_files).pack(side="left", padx=5)
        tk.Button(process_frame, text="Save Current Settings", command=self.save_current_settings).pack(side="left", padx=5)

    def refresh_models(self):
        global LMSTUDIO_URL
        LMSTUDIO_URL = self.server_entry.get()
        models = get_models()
        if models:
            self.model_dropdown['values'] = models
            self.model_dropdown.set(models[0])
        else:
            messagebox.showerror("Error", "Failed to fetch models from server.")

    def upload_files(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.uploaded_files = filenames
            self.files_listbox.delete(0, "end")
            for file in filenames:
                self.files_listbox.insert("end", os.path.basename(file))

    def select_output_dir(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_dir_var.set(dirname)

    def load_prompt_history(self):
        history = self.config.get("history", [])
        self.history_dropdown['values'] = [f"{h['prompt1'][:20]} | {h['prompt2'][:20]}" for h in history]

    def load_selected_prompt(self):
        idx = self.history_dropdown.current()
        if idx >= 0:
            selected = self.config["history"][idx]
            self.prompt1_text.delete("1.0", "end")
            self.prompt1_text.insert("1.0", selected["prompt1"])
            self.prompt2_text.delete("1.0", "end")
            self.prompt2_text.insert("1.0", selected["prompt2"])
            self.output_dir_var.set(selected["output_dir"])

    def save_current_settings(self):
        prompt1 = self.prompt1_text.get("1.0", "end").strip()
        prompt2 = self.prompt2_text.get("1.0", "end").strip()
        output_dir = self.output_dir_var.get()
        save_config(prompt1, prompt2, output_dir)
        messagebox.showinfo("Saved", "Settings saved to config.json.")

    def process_first_file(self):
        if not self.uploaded_files:
            messagebox.showerror("Error", "No files uploaded.")
            return

        def task():
            first_file = self.uploaded_files[0]
            with open(first_file, "r", encoding="utf-8") as f:
                content = f.read()

            prompt1 = self.prompt1_text.get("1.0", "end").strip()
            prompt2 = self.prompt2_text.get("1.0", "end").strip()
            server_url = self.server_entry.get()
            model_id = self.model_var.get()
            max_tokens = int(self.max_tokens_entry.get())

            output1 = process_file_content(content, prompt1, server_url, model_id, max_tokens)
            if output1:
                combined = content + output1 if self.include_source_var.get() else output1
                output2 = process_file_content(combined, prompt2, server_url, model_id, max_tokens)
                result = f"First Output:\n{output1}\n\nFinal Output:\n{output2}"
                self.show_result(result)
            else:
                self.show_result("Failed to process the first file.")

        threading.Thread(target=task).start()

    def process_all_files(self):
        if not self.uploaded_files:
            messagebox.showerror("Error", "No files uploaded.")
            return

        def task():
            prompt1 = self.prompt1_text.get("1.0", "end").strip()
            prompt2 = self.prompt2_text.get("1.0", "end").strip()
            server_url = self.server_entry.get()
            model_id = self.model_var.get()
            max_tokens = int(self.max_tokens_entry.get())

            output_dir = self.output_dir_var.get()
            first_output_dir = os.path.join(output_dir, "first_outputs")
            failed_output_dir = os.path.join(output_dir, "failed_files")

            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(first_output_dir, exist_ok=True)
            os.makedirs(failed_output_dir, exist_ok=True)

            for file in self.uploaded_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()

                    result1 = process_file_content(content, prompt1, server_url, model_id, max_tokens)
                    if result1:
                        with open(os.path.join(first_output_dir, f"first_output_{os.path.basename(file)}"), "w", encoding="utf-8") as f1:
                            f1.write(result1)

                        combined = content + result1 if self.include_source_var.get() else result1
                        result2 = process_file_content(combined, prompt2, server_url, model_id, max_tokens)

                        if result2:
                            with open(os.path.join(output_dir, f"processed_{os.path.basename(file)}"), "w", encoding="utf-8") as f2:
                                f2.write(result2)
                        else:
                            log_failed_file(file, "Second processing step failed.", failed_output_dir)
                    else:
                        log_failed_file(file, "First processing step failed.", failed_output_dir)
                except Exception as e:
                    log_failed_file(file, str(e), failed_output_dir)

            messagebox.showinfo("Completed", "All files processed and saved.")

        threading.Thread(target=task).start()

    def show_result(self, text):
        result_window = tk.Toplevel(self.root)
        result_window.title("Processing Result")
        txt = tk.Text(result_window, wrap="word")
        txt.pack(expand=True, fill="both")
        txt.insert("1.0", text)

def main():
    import tkinter as tk
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

