"""
GPT2 Trainer

Simple GPT2 Fine Tuning GUI

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, AutoConfig, DataCollatorForLanguageModeling
from datasets import Dataset
import json
import os
import threading
import statistics

CONFIG_FILE = "gpt_trainer_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "epochs": 3,
        "batch_size": 8,
        "learning_rate": 5e-5,
        "save_steps": 2500,
        "output_dir": "./ValheimGPT2_GUI"
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_custom_dataset(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sample = data[0]
    if 'question' in sample and 'answer' in sample:
        formatted_data = {'text': [f"Question: {entry['question']} Answer: {entry['answer']}" for entry in data]}
    elif 'prompt' in sample and 'response' in sample:
        formatted_data = {'text': [f"Prompt: {entry['prompt']} Response: {entry['response']}" for entry in data]}
    else:
        raise ValueError("Unsupported data format. Must contain 'question'/'answer' or 'prompt'/'response'.")
    
    return Dataset.from_dict(formatted_data), data

def suggest_settings(json_path):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'question' in data[0] and 'answer' in data[0]:
        texts = [f"Question: {item['question']} Answer: {item['answer']}" for item in data]
    elif 'prompt' in data[0] and 'response' in data[0]:
        texts = [f"Prompt: {item['prompt']} Response: {item['response']}" for item in data]
    else:
        raise ValueError("Unsupported data format for suggestions.")

    token_counts = [len(tokenizer.encode(text)) for text in texts]
    avg_tokens = int(statistics.mean(token_counts))
    total_tokens = avg_tokens * len(texts)

    if len(texts) < 1000:
        return {"epochs": 5, "batch_size": 4, "learning_rate": 5e-5, "save_steps": 100}
    elif len(texts) < 10000:
        return {"epochs": 3, "batch_size": 8, "learning_rate": 3e-5, "save_steps": 250}
    else:
        return {"epochs": 2, "batch_size": 16, "learning_rate": 2e-5, "save_steps": 500}

def start_training(json_path, config):
    try:
        save_config(config)

        dataset, _ = load_custom_dataset(json_path)
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token

        def tokenize_function(examples):
            return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        split = tokenized_dataset.train_test_split(test_size=0.2)
        train_dataset = split['train']
        eval_dataset = split['test']

        model_config = AutoConfig.from_pretrained("gpt2")
        model_config.vocab_size = len(tokenizer)
        model = AutoModelForCausalLM.from_config(model_config)

        training_args = TrainingArguments(
            output_dir=config["output_dir"],
            evaluation_strategy="steps",
            learning_rate=float(config["learning_rate"]),
            weight_decay=0.01,
            save_steps=int(config["save_steps"]),
            num_train_epochs=int(config["epochs"]),
            per_device_train_batch_size=int(config["batch_size"]),
            per_device_eval_batch_size=int(config["batch_size"]),
            logging_dir="./logs",
            logging_steps=int(config["save_steps"]),
            save_total_limit=3
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )

        trainer.train()
        trainer.save_model(config["output_dir"])
        tokenizer.save_pretrained(config["output_dir"])
        messagebox.showinfo("Success", f"Training complete! Model saved to {config['output_dir']}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def launch_gui():
    config_data = load_config()

    def browse_json():
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            json_entry.delete(0, tk.END)
            json_entry.insert(0, path)

    def browse_output_dir():
        path = filedialog.askdirectory()
        if path:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, path)

    def run_training():
        path = json_entry.get()
        if not os.path.isfile(path):
            messagebox.showerror("File Error", "Please select a valid training JSON file.")
            return

        config = {
            "epochs": int(epochs_entry.get()),
            "batch_size": int(batch_entry.get()),
            "learning_rate": float(lr_entry.get()),
            "save_steps": int(save_steps_entry.get()),
            "output_dir": output_entry.get()
        }

        if not os.path.isdir(config["output_dir"]):
            os.makedirs(config["output_dir"])

        threading.Thread(target=start_training, args=(path, config)).start()

    def apply_suggested_settings():
        path = json_entry.get()
        if not os.path.isfile(path):
            messagebox.showerror("File Error", "Select a valid file first.")
            return
        try:
            suggestions = suggest_settings(path)
            epochs_entry.delete(0, tk.END)
            epochs_entry.insert(0, suggestions["epochs"])
            batch_entry.delete(0, tk.END)
            batch_entry.insert(0, suggestions["batch_size"])
            lr_entry.delete(0, tk.END)
            lr_entry.insert(0, suggestions["learning_rate"])
            save_steps_entry.delete(0, tk.END)
            save_steps_entry.insert(0, suggestions["save_steps"])
            messagebox.showinfo("Suggestions Applied", "Suggested settings have been applied.")
        except Exception as e:
            messagebox.showerror("Suggestion Error", str(e))

    root = tk.Tk()
    root.title("GPT-2 Trainer")

    tk.Label(root, text="Training JSON File:").pack()
    json_entry = tk.Entry(root, width=60)
    json_entry.pack()
    tk.Button(root, text="Browse...", command=browse_json).pack(pady=5)

    tk.Label(root, text="Output Directory:").pack()
    output_entry = tk.Entry(root, width=60)
    output_entry.insert(0, config_data.get("output_dir", ""))
    output_entry.pack()
    tk.Button(root, text="Select Folder", command=browse_output_dir).pack(pady=5)

    tk.Label(root, text="Training Settings:").pack(pady=10)
    settings_frame = tk.Frame(root)
    settings_frame.pack()

    tk.Label(settings_frame, text="Epochs").grid(row=0, column=0)
    epochs_entry = tk.Entry(settings_frame, width=5)
    epochs_entry.insert(0, config_data.get("epochs", 3))
    epochs_entry.grid(row=0, column=1, padx=10)

    tk.Label(settings_frame, text="Batch Size").grid(row=0, column=2)
    batch_entry = tk.Entry(settings_frame, width=5)
    batch_entry.insert(0, config_data.get("batch_size", 8))
    batch_entry.grid(row=0, column=3, padx=10)

    tk.Label(settings_frame, text="Learning Rate").grid(row=1, column=0)
    lr_entry = tk.Entry(settings_frame, width=8)
    lr_entry.insert(0, config_data.get("learning_rate", 5e-5))
    lr_entry.grid(row=1, column=1, padx=10)

    tk.Label(settings_frame, text="Save Steps").grid(row=1, column=2)
    save_steps_entry = tk.Entry(settings_frame, width=8)
    save_steps_entry.insert(0, config_data.get("save_steps", 2500))
    save_steps_entry.grid(row=1, column=3, padx=10)

    tk.Button(root, text="Suggest Settings", command=apply_suggested_settings).pack(pady=5)
    tk.Button(root, text="Start Training", command=run_training, bg="green", fg="white").pack(pady=10)

    root.mainloop()

def main():
    launch_gui()

if __name__ == "__main__":
    main()