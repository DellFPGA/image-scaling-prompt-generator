# 🎨 Image Scaling & Prompt Generator

An intelligent, interactive prompt-generation toolkit for AI artists using **Stable Diffusion** (txt2img / img2img). Designed to build highly structured, enhanced prompts with optional LLM support via [Ollama](https://ollama.com/).  

Created with love and logic by **NG60-AI-Creator**.

---

## 🚀 Features

- 🖌️ Structured prompt crafting: genres, styles, descriptors, artists
- 📏 VRAM-aware scaling logic for image-to-image workflows
- 🧠 Local LLM support (via `ollama`) for refining prompts
- 🔧 Built-in config editor and safe-mode fallback
- 📝 Automatically logs all prompt generations
- 🔁 JSON config backup/restore built-in
- 🧰 Optional tools to sync `stable` branch with release tags

---

## 💻 Requirements

- Python 3.6+
- Compatible with Windows, Linux, macOS
- Optional: [`ollama`](https://ollama.com/) with local LLMs
- Optional: NVIDIA GPU (tested on RTX 8000)

---

## 🧪 How to Use

Generate prompt

Choose one or more options per category (or use random/custom)

Optionally enhance the prompt with a local LLM

Review & save the result

Prompts are saved in generated_prompts.txt.

🗂 Configuration
All categories are defined in the config/ folder:

artists.json

genres.json

rendering.json

descriptors.json

negative.json

Edit using the script menu or directly in the files. All edits are auto-backed up to config/_backup/.

🤖 LLM Support
Auto-detects installed models (like llama3, mistral)

Sends positive/negative prompt pairs to the LLM

Blocks and exits gracefully if safety rails are triggered

Powered locally with Ollama for maximum privacy and control.

📎 Related Projects
🛠 image-scaling-tool: AI-friendly image resizer with aspect ratio constraints

📚 Docs & Wiki
📘 See the Wiki for help, setup, config info, and usage examples.

🪪 License
MIT License — free to use, fork, and modify.

Built by NG60-AI-Creator for artists, engineers, and AI enthusiasts.
