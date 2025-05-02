"""
Extension Changer Tool

Batch-renames files from one extension to another in a selected folder.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import os
import tkinter as tk
from tkinter import filedialog, messagebox

def batch_rename_files(directory, old_ext, new_ext, log_callback=print):
    """Renames all files in the given directory with the old extension to the new one."""
    if not old_ext.startswith("."):
        old_ext = "." + old_ext
    if not new_ext.startswith("."):
        new_ext = "." + new_ext

    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(old_ext):
            new_filename = filename[:-len(old_ext)] + new_ext
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            log_callback(f"Renamed: {filename} -> {new_filename}")
            count += 1

    log_callback(f"\n✔ Renamed {count} file(s) in '{directory}'.")

def browse_folder(entry_field):
    """Opens a folder selection dialog and updates the entry field."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, folder_path)

def run_gui_clean(folder_entry, old_ext_entry, new_ext_entry, log_text):
    folder = folder_entry.get()
    old_ext = old_ext_entry.get().strip()
    new_ext = new_ext_entry.get().strip()

    if not os.path.isdir(folder):
        messagebox.showerror("Invalid Folder", "The selected folder doesn't exist.")
        return
    if not old_ext or not new_ext:
        messagebox.showwarning("Missing Extensions", "Please provide both old and new extensions.")
        return

    batch_rename_files(folder, old_ext, new_ext, log_text.set)

def start_gui():
    """Launches the Tkinter GUI."""
    root = tk.Tk()
    root.title("Extension Changer")

    tk.Label(root, text="Target Folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    folder_entry = tk.Entry(root, width=50)
    folder_entry.grid(row=0, column=1, padx=5)
    folder_entry.insert(0, os.getcwd())
    tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry)).grid(row=0, column=2, padx=5)

    tk.Label(root, text="Old Extension (e.g. .txt):").grid(row=1, column=0, sticky="w", padx=5)
    old_ext_entry = tk.Entry(root, width=20)
    old_ext_entry.grid(row=1, column=1, sticky="w", padx=5)

    tk.Label(root, text="New Extension (e.g. .md):").grid(row=2, column=0, sticky="w", padx=5)
    new_ext_entry = tk.Entry(root, width=20)
    new_ext_entry.grid(row=2, column=1, sticky="w", padx=5)

    log_text = tk.StringVar()
    tk.Label(root, textvariable=log_text, fg="blue", justify="left", wraplength=420).grid(row=4, column=0, columnspan=3, pady=10)

    tk.Button(root, text="Rename Files", command=lambda: run_gui_clean(folder_entry, old_ext_entry, new_ext_entry, log_text)).grid(row=3, column=1, pady=10)

    root.mainloop()

def main():
    """Entry point when run as a CLI tool via flit."""
    start_gui()

if __name__ == "__main__":
    main()
