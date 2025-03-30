"""
Author: devall6@yahoo.com
Version: 1.1

Description:
Interactive prompt generator for AI art using Stable Diffusion (text2img or img2img).
Allows the user to construct a high-quality positive and negative prompt based on structured questions,
with optional enhancement using a locally installed LLM via Ollama. All prompts are logged to file for 
tracking progress and documentation of image generations. Users can also edit configuration categories 
(artists, genres, descriptors, etc.) through a built-in menu. Backup and undo options are also supported.

Target System:
Runs on a Dell PowerEdge server with NVIDIA RTX-8000 GPU (or other compatible NVIDIA GPUs).

"""

import os
import json
import subprocess
import random
from datetime import datetime
import sys
import shutil

# ========== Constants and File Paths ==========
OUTPUT_LOG = "generated_prompts.txt"
CONFIG_DIR = "config"
BACKUP_DIR = os.path.join(CONFIG_DIR, "_backup")
CATEGORY_FILES = {
    "descriptors": os.path.join(CONFIG_DIR, "descriptors.json"),
    "negative": os.path.join(CONFIG_DIR, "negative.json"),
    "rendering": os.path.join(CONFIG_DIR, "rendering.json"),
    "genres": os.path.join(CONFIG_DIR, "genres.json"),
    "artists": os.path.join(CONFIG_DIR, "artists.json")
}

# ========== Ollama Utilities ==========
def is_ollama_installed():
    return subprocess.call(["which", "ollama"], stdout=subprocess.DEVNULL) == 0

def get_ollama_models():
    try:
        result = subprocess.check_output(["ollama", "list"], text=True)
        lines = result.strip().split("\n")[1:]  # skip header
        models = [line.split()[0] for line in lines]
        return models
    except Exception:
        return []

def simulate_llm_check(prompt_text, model_name):
    blocked_terms = ["nudity", "violence", "sexually explicit", "offensive"]
    if any(term in prompt_text.lower() for term in blocked_terms):
        print(f"\n⚠️ The selected LLM model '{model_name}' blocked the request due to community safety guidelines.")
        print("Your input may violate the model's restrictions. Please try again using a different model or with safer terms.")
        sys.exit(1)

# ========== File Utilities ==========
def clean_input(entry):
    return entry.replace("'", "").replace('"', '').strip()

def load_category(category):
    path = CATEGORY_FILES[category]
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_category(category, data):
    path = CATEGORY_FILES[category]
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"{category}.bak.json")
    if os.path.exists(path):
        shutil.copy(path, backup_path)
    with open(path, "w") as f:
        json.dump(sorted(list(set(data))), f, indent=2)

def restore_backup(category):
    backup_path = os.path.join(BACKUP_DIR, f"{category}.bak.json")
    original_path = CATEGORY_FILES[category]
    if os.path.exists(backup_path):
        shutil.copy(backup_path, original_path)
        print(f"✔️ Restored backup for '{category}'")
    else:
        print(f"⚠️ No backup found for '{category}'")

# ========== Prompt Building Logic ==========
def ask_multiple(prompt, options, page_size=10):
    print(f"\n{prompt}")
    for i in range(0, len(options), page_size):
        chunk = options[i:i+page_size]
        for idx, opt in enumerate(chunk, i+1):
            print(f"  [{idx}] {opt}")
        if i + page_size < len(options):
            input("-- Press Enter to see more options --")
    print("\nYou may:")
    print("- Enter one or more numbers separated by commas")
    print("- Type 'random' to select randomly")
    print("- Type custom terms directly")
    choice = input("Enter your selection: ").strip()
    if choice.lower() == 'random':
        return random.sample(options, k=min(3, len(options)))
    entries = [clean_input(item) for item in choice.split(',') if item.strip()]
    result = []
    for entry in entries:
        if entry.isdigit() and 1 <= int(entry) <= len(options):
            result.append(options[int(entry) - 1])
        else:
            result.append(entry)
    return result

# ========== Category Editor ==========
def edit_categories():
    while True:
        print("\n--- Edit Configuration Categories ---")
        for i, cat in enumerate(CATEGORY_FILES.keys(), 1):
            print(f"  [{i}] {cat}")
        print("  [R] Restore last backup")
        print("  [0] Back to main menu")
        choice = input("Choose a category to edit: ").strip().lower()
        if choice == '0':
            return
        elif choice == 'r':
            target = input("Which category to restore from backup? ").strip().lower()
            if target in CATEGORY_FILES:
                restore_backup(target)
            else:
                print("Invalid category.")
        elif choice.isdigit() and 1 <= int(choice) <= len(CATEGORY_FILES):
            category = list(CATEGORY_FILES.keys())[int(choice) - 1]
            items = load_category(category)
            print(f"\nCurrent entries in '{category}':")
            for i, item in enumerate(items, 1):
                print(f"  [{i}] {item}")
            action = input("Type 'add' to add new item(s), 'remove' to delete, or Enter to skip: ").strip().lower()
            if action == 'add':
                new_items = input("Enter new item(s) separated by commas: ").split(',')
                items.extend([clean_input(i) for i in new_items])
            elif action == 'remove':
                to_remove = input("Enter number(s) of items to remove separated by commas: ").split(',')
                for num in sorted([int(n) for n in to_remove if n.isdigit()], reverse=True):
                    if 1 <= num <= len(items):
                        del items[num - 1]
            save_category(category, items)
            print(f"Updated '{category}' saved.")

# ========== Prompt Generator ==========
def generate_prompt():
    print("\n=== Stable Diffusion Prompt Generator ===")

    use_llm = False
    selected_model = None
    if is_ollama_installed():
        models = get_ollama_models()
        if models:
            print("\nAvailable Ollama Models:")
            for i, model in enumerate(models):
                print(f"  [{i+1}] {model}")
            model_idx = input("Choose a model number to enhance prompt (or press Enter to skip): ")
            if model_idx.isdigit() and 1 <= int(model_idx) <= len(models):
                selected_model = models[int(model_idx) - 1]
                use_llm = True
        else:
            print("No models found. Continuing without LLM.")
    else:
        print("Ollama not installed. Continuing without LLM.")

    categories = {cat: load_category(cat) for cat in CATEGORY_FILES.keys()}

    subject = ask_multiple("Is this a picture of a person, place, or thing?", ["person", "place", "thing"])[0]
    genre = ask_multiple("Choose one or more genres:", categories['genres'])
    artist = ask_multiple("Choose one or more artists:", categories['artists'])
    rendering = ask_multiple("Choose one or more rendering styles:", categories['rendering'])
    descriptors = ask_multiple("Choose descriptive terms:", categories['descriptors'])
    negatives = categories['negative']
    scene = input("\nDescribe the scene (will be emphasized with parentheses): ")

    pos_prompt = f"(masterpiece, high quality), ({subject}), "
    pos_prompt += ", ".join(genre) + ", "
    pos_prompt += "by " + ", by ".join(artist) + ", "
    pos_prompt += "rendered in " + ", rendered in ".join(rendering) + ", "
    pos_prompt += ", ".join([f"({d})" for d in descriptors]) + f", ({scene})"
    neg_prompt = ", ".join(negatives)

    if use_llm and selected_model:
        simulate_llm_check(pos_prompt + neg_prompt, selected_model)

    with open(OUTPUT_LOG, "a") as f:
        f.write(f"\n[{datetime.now()}]\n")
        f.write("Positive Prompt:\n" + pos_prompt + "\n")
        f.write("Negative Prompt:\n" + neg_prompt + "\n")
        f.write("-" * 60 + "\n")

    print("\n✅ Prompt generated!")
    print("Positive Prompt:\n", pos_prompt)
    print("Negative Prompt:\n", neg_prompt)

    if use_llm and selected_model:
        print(f"\n🤖 [Optional] You can now pass this prompt to '{selected_model}' using Ollama CLI if desired.")

# ========== Main Menu ==========
def main():
    while True:
        print("\n=== MAIN MENU ===")
        print("[1] Generate a prompt")
        print("[2] Edit categories")
        print("[3] Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            generate_prompt()
        elif choice == '2':
            edit_categories()
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
