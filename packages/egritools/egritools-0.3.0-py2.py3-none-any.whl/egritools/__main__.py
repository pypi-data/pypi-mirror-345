import subprocess

def main():
    print("""
🧰 EGRIGOR'S TOOLKIT
=======================
1. Change File Extensions
2. Create Python Venv
3. Upload to HuggingFace
4. Preclean JSON Files
5. Offline Wheel Manager
6. GPT2 Trainer
7. Combine TXT
8. Launcher
9. File Processor
0. Exit
""")
    choice = input("Pick a tool (1-7): ").strip()

    commands = {
        "1": "change-extension",
        "2": "create-venv",
        "3": "hf-upload",
        "4": "preclean-gui",
        "5": "wheel-manager",
        "6": "gpt2-trainer",
        "7": "combine-txt",
        "8": "launcher-gui",
        "9": "file_processor",
    }

    if choice in commands:
        subprocess.run(commands[choice], shell=True)
    elif choice == "0":
        print("Goodbye.")
    else:
        print("Invalid selection.")
