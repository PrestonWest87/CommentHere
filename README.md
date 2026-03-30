# CommentHere

**CommentHere** is a Python-based desktop tool that automatically scans your project directories and injects concise, AI-generated explanations into your source code. 

Instead of blindly guessing where to put comments, it uses **Tree-sitter** to accurately parse the Abstract Syntax Tree (AST) of your code. It identifies major structural nodes (like classes, functions, and methods) that are currently missing comments, asks a local LLM (via Ollama) to explain them, and neatly injects the documentation directly into your files.

## ✨ Features
* **Polyglot Support:** Works seamlessly across 11 major programming languages and markup formats.
* **AST Precision:** Uses Tree-sitter to surgically target functions, classes, and methods, ignoring irrelevant boilerplate.
* **Smart Detection:** Skips code blocks that already have comments directly above them.
* **Local & Private AI:** Uses Ollama to generate comments locally. Your proprietary code never leaves your network.
* **Safe Execution:** Automatically generates `.bak` backup files for every file it modifies.
* **Simple GUI:** Built-in Tkinter interface to easily select directories and monitor execution logs.

## 🛠 Supported Languages
* Python (`.py`)
* JavaScript (`.js`)
* TypeScript (`.ts`)
* Java (`.java`)
* C (`.c`)
* C++ (`.cpp`)
* C# (`.cs`)
* Ruby (`.rb`)
* PHP (`.php`)
* HTML (`.html`)
* CSS (`.css`)

## 🚀 Prerequisites

1. **Python 3.8+**
2. **Ollama:** You must have [Ollama](https://ollama.com/) installed and running on your network/machine.
3. **An LLM Model:** By default, the script looks for `phi4-mini:3.8b-q4_K_M`. You can pull it or any other model you prefer:
   ```bash
   ollama run phi4-mini:3.8b-q4_K_M
   ```

## 📦 Installation

1. Clone the **CommentHere** repository:
   ```bash
   git clone https://github.com/yourusername/CommentHere.git
   cd CommentHere
   ```
2. Install the required Python dependencies. You will need the `requests` library and the language-specific Tree-sitter bindings:
   ```bash
   pip install requests tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-html tree-sitter-css tree-sitter-java tree-sitter-c tree-sitter-cpp tree-sitter-c-sharp tree-sitter-ruby tree-sitter-php
   ```

## ⚙️ Configuration

Before running the script, open it in your text editor and update the **Configuration** section to match your Ollama setup.

```python
# --- Configuration ---
# Change this to 'http://localhost:11434/api/generate' if running on the same machine
OLLAMA_URL = "http://192.168.1.148:11434/api/generate" 

# Change this to your preferred model (e.g., 'llama3', 'mistral', or 'phi3')
MODEL_NAME = "phi4-mini:3.8b-q4_K_M"
```

## 💻 Usage

1. Run the script from your terminal:
   ```bash
   python main.py
   ```
   *(Note: Replace `main.py` with the actual filename of your script if it's named differently).*
2. The GUI will appear. Click **"Browse Folder"** and select the root directory of the codebase you want to comment.
3. Click **"Run AI Commenter"**.
4. Watch the execution logs in the middle pane. The script will output which files it is scanning, how many undocumented blocks it found, and whether the injection was successful.

## ⚠️ Important Notes & Safety

* **Backups:** For every file modified, the script creates a backup of the original code in the same directory (e.g., `script.py.bak`). If you don't like the AI's comments, you can easily restore your old files.
* **AI Hallucinations:** The quality of the comments depends entirely on the LLM you use. Always review the AI-generated comments to ensure accuracy before committing changes to version control.
* **Truncation:** To save context window space and processing time, if a code block (like a massive class) exceeds 1,000 characters, it is truncated before being sent to the AI.
