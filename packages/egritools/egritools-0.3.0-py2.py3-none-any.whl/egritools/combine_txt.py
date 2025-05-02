"""
TXT File Combiner

Combines all the txt files in a chosen directory into a single txt file.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

def combine_text_files(folder_path, output_file_name, progress_bar, status_label):
    # Ensure output file name is not empty or invalid
    if not output_file_name:
        messagebox.showerror("Error", "Please provide a valid output file name.")
        return

    # Get the current directory where the script was launched from
    current_directory = os.getcwd()

    # Set the output file path to be in the current directory
    output_file_path = os.path.join(current_directory, output_file_name)

    try:
        # Open the output file in write mode
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Get the list of files to combine
            txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
            total_files = len(txt_files)

            if total_files == 0:
                messagebox.showwarning("Warning", "No text files found in the selected folder.")
                return

            # Start the progress bar
            progress_bar['maximum'] = total_files
            progress_bar['value'] = 0

            # Write content from each file to the output file
            for idx, filename in enumerate(txt_files):
                file_path = os.path.join(folder_path, filename)
                # Open and read the content of the current text file
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    content = input_file.read()
                    # Write the content to the output file
                    output_file.write(content)
                    # Add a newline to separate contents of different files
                    output_file.write('\n')
                
                # Update the progress bar and status label
                progress_bar['value'] = idx + 1
                status_label.config(text=f"Combining: {idx + 1}/{total_files} files")
                root.update_idletasks()  # Update the GUI

        messagebox.showinfo("Success", f"All text files have been combined into {output_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def browse_for_folder(entry_folder_path):
    # Ask the user to select a folder containing the .txt files
    folder_path = filedialog.askdirectory(title="Select Folder Containing Text Files")
    if folder_path:
        entry_folder_path.delete(0, tk.END)  # Clear current path in the entry
        entry_folder_path.insert(0, folder_path)  # Insert the new folder path

def save_output_as(entry_output_filename):
    # Allow the user to provide a custom output filename
    output_filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if output_filename:
        entry_output_filename.delete(0, tk.END)  # Clear current output filename in the entry
        entry_output_filename.insert(0, output_filename)  # Insert the new output filename

def main():
    # Create the root window
    global root
    root = tk.Tk()
    root.title("Text File Combiner")

    # Set the window size
    root.geometry("500x350")

    # Create a label
    label = tk.Label(root, text="Combine all .txt files in a folder into one.", font=("Arial", 12))
    label.pack(pady=20)

    # Folder selection entry
    label_folder_path = tk.Label(root, text="Select Folder:")
    label_folder_path.pack()
    entry_folder_path = tk.Entry(root, width=50)
    entry_folder_path.insert(0, os.getcwd())  # Default to current working directory
    entry_folder_path.pack(pady=5)
    browse_button = tk.Button(root, text="Browse", command=lambda: browse_for_folder(entry_folder_path))
    browse_button.pack(pady=5)

    # Output filename entry
    label_output_filename = tk.Label(root, text="Enter Output Filename (default: 'combined_output.txt'):")
    label_output_filename.pack()
    entry_output_filename = tk.Entry(root, width=50)
    entry_output_filename.insert(0, "combined_output.txt")  # Default output filename
    entry_output_filename.pack(pady=5)
    save_button = tk.Button(root, text="Save As", command=lambda: save_output_as(entry_output_filename))
    save_button.pack(pady=5)

    # Combine button to start combining the files
    combine_button = tk.Button(root, text="Combine Files", command=lambda: combine_text_files(
        entry_folder_path.get(), entry_output_filename.get(), progress_bar, status_label), font=("Arial", 14))
    combine_button.pack(pady=20)

    # Create a progress bar
    progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    # Create a status label to show the current progress
    status_label = tk.Label(root, text="Combining: 0/0 files", font=("Arial", 10))
    status_label.pack(pady=10)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
