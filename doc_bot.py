import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tree_sitter import Language, Parser

# --- Import All Supported Tree-sitter Languages ---
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_html as tshtml
import tree_sitter_css as tscss
import tree_sitter_java as tsjava
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_c_sharp as tscsharp
import tree_sitter_ruby as tsruby
import tree_sitter_php as tsphp

# --- Configuration ---
OLLAMA_URL = "http://192.168.1.148:11434/api/generate"
MODEL_NAME = "phi4-mini:3.8b-q4_K_M"

# The Universal Language Dictionary
# Maps extensions to their parser, comment style, and the AST nodes we want to comment on.
LANGUAGE_CONFIG = {
    '.py': {
        'ts_language': Language(tspython.language()),
        'prefix': '# ', 'suffix': '',
        'nodes': ['function_definition', 'class_definition']
    },
    '.js': {
        'ts_language': Language(tsjavascript.language()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['function_declaration', 'class_declaration', 'arrow_function']
    },
    '.ts': {
        'ts_language': Language(tstypescript.language_typescript()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['function_declaration', 'class_declaration', 'method_definition']
    },
    '.java': {
        'ts_language': Language(tsjava.language()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['method_declaration', 'class_declaration']
    },
    '.c': {
        'ts_language': Language(tsc.language()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['function_definition', 'struct_specifier']
    },
    '.cpp': {
        'ts_language': Language(tscpp.language()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['function_definition', 'class_specifier']
    },
    '.cs': {
        'ts_language': Language(tscsharp.language()),
        'prefix': '// ', 'suffix': '',
        'nodes': ['method_declaration', 'class_declaration']
    },
    '.rb': {
        'ts_language': Language(tsruby.language()),
        'prefix': '# ', 'suffix': '',
        'nodes': ['method', 'class']
    },
    '.php': {
        'ts_language': Language(tsphp.language_php()), 
        'prefix': '// ', 'suffix': '',
        'nodes': ['function_definition', 'class_declaration', 'method_declaration']
    },
    '.html': {
        'ts_language': Language(tshtml.language()),
        'prefix': '',
        'nodes': ['script_element', 'style_element'] # Usually best to just comment major blocks in HTML
    },
    '.css': {
        'ts_language': Language(tscss.language()),
        'prefix': '/* ', 'suffix': ' */',
        'nodes': ['rule_set']
    }
}

class AIBatchCommenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal AI Batch Commenter")
        self.root.geometry("700x550")
        self.target_directory = ""
        self.setup_ui()

    def setup_ui(self):
        # Top Frame
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X, padx=20)

        self.lbl_dir = tk.Label(top_frame, text="No directory selected", fg="gray", font=("Arial", 10, "italic"))
        self.lbl_dir.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_browse = tk.Button(top_frame, text="Browse Folder", command=self.select_directory, bg="#e0e0e0")
        btn_browse.pack(side=tk.RIGHT, padx=5)

        # Middle Frame
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(mid_frame, text="Execution Logs:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(mid_frame, height=18, state='disabled', bg="#1e1e1e", fg="#4CAF50", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Bottom Frame
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill=tk.X, padx=20)

        btn_run = tk.Button(bottom_frame, text="Run AI Commenter", command=self.run_batch, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        btn_run.pack(fill=tk.X, pady=5)

    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update()

    def select_directory(self):
        folder_selected = filedialog.askdirectory(title="Select Target Directory")
        if folder_selected:
            self.target_directory = folder_selected
            self.lbl_dir.config(text=self.target_directory, fg="black", font=("Arial", 10))
            self.log_message(f"Selected directory: {self.target_directory}")

    def clean_llm_output(self, raw_text):
        """Strips markdown formatting from Ollama."""
        text = raw_text.replace("```", "")
        text = text.replace('"""', '').replace("'''", '')
        # Grab just the first meaningful sentence/line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines[0] if lines else "Processed block."

    def generate_inline_comment(self, code_snippet, lang_ext):
        """Asks Ollama for a concise explanation."""
        prompt = (
            f"Write a concise technical explanation of what this {lang_ext} code block does. "
            "Return ONLY the raw text. DO NOT use markdown. "
            f"Code:\n{code_snippet}"
        )

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": 2048}
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            raw_doc = response.json().get("response", "")
            return self.clean_llm_output(raw_doc)
        except Exception as e:
            self.log_message(f"    [!] Ollama API Error: {e}")
            return "TODO: AI comment generation failed."

    def collect_target_nodes(self, node, target_types, nodes_list):
        """Walks the AST looking for specific node types."""
        if node.type in target_types:
            # Check if it already has a comment right above it
            if not (node.prev_sibling and 'comment' in node.prev_sibling.type.lower()):
                nodes_list.append(node)

        for child in node.children:
            self.collect_target_nodes(child, target_types, nodes_list)

    def process_file(self, filepath, config, ext):
        self.log_message(f"Scanning {os.path.basename(filepath)}...")
        
        parser = Parser(config['ts_language'])
        
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        source_bytes = bytes(source_code, "utf8")
        tree = parser.parse(source_bytes)
        
        nodes_to_document = []
        self.collect_target_nodes(tree.root_node, config['nodes'], nodes_to_document)
        
        if not nodes_to_document:
            self.log_message("  -> No undocumented code blocks found.")
            return False

        self.log_message(f"  -> Found {len(nodes_to_document)} blocks. Generating comments...")
        
        edits = []
        for node in nodes_to_document:
            block_code = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
            if len(block_code) > 1000:
                block_code = block_code[:1000] + "\n...[truncated]"

            llm_text = self.generate_inline_comment(block_code, ext)
            
            indent_level = node.start_point[1]
            indent_str = " " * indent_level
            
            # Format injection with prefix and suffix support
            comment_line = f"{config.get('prefix', '')}{llm_text}{config.get('suffix', '')}"
            injection = f"{comment_line}\n{indent_str}"
            
            edits.append((node.start_byte, injection))

        # Bottom-Up Injection
        edits.sort(key=lambda x: x[0], reverse=True)
        
        final_bytes = source_bytes
        for pos, injection in edits:
            final_bytes = final_bytes[:pos] + injection.encode('utf-8') + final_bytes[pos:]

        # Backup & Save
        backup_path = filepath + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(source_code)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_bytes.decode('utf-8'))
            
        self.log_message("  -> Success! Comments injected.")
        return True

    def run_batch(self):
        if not self.target_directory:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return

        self.log_message("\n--- Starting Polyglot Batch Process ---")
        processed, skipped = 0, 0

        for root_dir, _, files in os.walk(self.target_directory):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in LANGUAGE_CONFIG:
                    filepath = os.path.join(root_dir, filename)
                    if self.process_file(filepath, LANGUAGE_CONFIG[ext], ext):
                        processed += 1
                    else:
                        skipped += 1

        self.log_message(f"\n--- Process Complete ---")
        self.log_message(f"Files Modified: {processed} | Files Skipped/Unchanged: {skipped}\n")
        messagebox.showinfo("Complete", f"Processing finished.\nModified: {processed}\nSkipped: {skipped}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AIBatchCommenterApp(root)
    root.mainloop()