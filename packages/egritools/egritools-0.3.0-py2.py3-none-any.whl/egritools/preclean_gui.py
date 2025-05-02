"""
Preclean Json Arrays

Cleans the data from before the first { and last } in a json file.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import os
import tkinter as tk
from tkinter import filedialog, messagebox

def clean_json_files(input_folder, log_callback):
    cleaned_count = 0
    skipped_files = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                start_index = content.find("{")
                end_index = content.rfind("}") + 1

                if start_index == -1 or end_index == 0:
                    skipped_files.append(filename)
                    continue

                cleaned_content = content[start_index:end_index]

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned_content)

                cleaned_count += 1
            except Exception as e:
                log_callback(f"Error processing {filename}: {e}")

    log_callback(f"\n✔ Cleaned {cleaned_count} file(s).")
    if skipped_files:
        log_callback(f"⚠ Skipped files (no valid JSON): {', '.join(skipped_files)}")

def browse_folder(entry_field):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, folder_path)

def run_cleaner(folder_path, log_callback):
    if not os.path.isdir(folder_path):
        messagebox.showerror("Invalid Folder", "Please select a valid folder.")
        return
    clean_json_files(folder_path, log_callback)

# GUI Setup
def start_gui():
    root = tk.Tk()
    root.title("JSON Precleaner GUI")

    tk.Label(root, text="Select Folder to Clean:").pack(pady=5)
    folder_entry = tk.Entry(root, width=50)
    folder_entry.pack(padx=10)

    tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry)).pack(pady=2)
    log_text = tk.StringVar()
    tk.Label(root, textvariable=log_text, wraplength=400, justify="left", fg="blue").pack(pady=10)

    tk.Button(root, text="Start Cleaning", command=lambda: run_cleaner(folder_entry.get(), lambda msg: log_text.set(msg))).pack(pady=10)

    root.mainloop()

def main():
    """Launches the precleaner GUI via command line."""
    start_gui()

if __name__ == "__main__":
    main()
