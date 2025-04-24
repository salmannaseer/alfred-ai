import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import requests
import json
import threading
import fitz  # PyMuPDF
from docx import Document

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Alfred AI")
        self.state("zoomed")

        self.chat_history = []
        self.context_attachment = ""
        self.font_size = 12
        self.font_family = "Segoe UI"
        self.last_ai_response = ""

        # === Top Toolbar ===
        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X, padx=10, pady=(5, 0))

        spacer = tk.Label(toolbar, text="")
        spacer.pack(side=tk.LEFT, expand=True)

        self.export_button = tk.Button(toolbar, text="Export Chat", command=self.export_chat)
        self.export_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.copy_button = tk.Button(toolbar, text="Copy Last Response", command=self.copy_last_response)
        self.copy_button.pack(side=tk.RIGHT, padx=(5, 0))

        decrease_btn = tk.Button(toolbar, text="A-", command=self.decrease_font)
        decrease_btn.pack(side=tk.RIGHT, padx=(5, 0))

        increase_btn = tk.Button(toolbar, text="A+", command=self.increase_font)
        increase_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.font_dropdown = ttk.Combobox(toolbar, values=[
            "Comic Sans MS", "Segoe UI", "Times New Roman", "Arial", "Calibri", "sans-serif"
        ], state="readonly")
        self.font_dropdown.set(self.font_family)
        self.font_dropdown.pack(side=tk.RIGHT, padx=(5, 0))
        self.font_dropdown.bind("<<ComboboxSelected>>", self.change_font)

        # === Output Field ===
        self.output_field = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=(self.font_family, self.font_size))
        self.output_field.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.output_field.tag_configure("bold", font=(self.font_family, self.font_size, "bold"))

        # === Input Frame ===
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)
        self.input_frame.columnconfigure(0, weight=1)

        self.input_field = tk.Entry(self.input_frame)
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_field.bind("<Return>", lambda event: self.send_request())

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_request, width=10)
        self.send_button.grid(row=0, column=1, padx=(5, 5))

        self.attach_button = tk.Button(self.input_frame, text="Attach", command=self.upload_file, width=10)
        self.attach_button.grid(row=0, column=2)

    def change_font(self, event=None):
        self.font_family = self.font_dropdown.get()
        self.output_field.configure(font=(self.font_family, self.font_size))
        self.output_field.tag_configure("bold", font=(self.font_family, self.font_size, "bold"))

    def increase_font(self):
        self.font_size += 1
        self.output_field.configure(font=(self.font_family, self.font_size))
        self.output_field.tag_configure("bold", font=(self.font_family, self.font_size, "bold"))

    def decrease_font(self):
        self.font_size = max(8, self.font_size - 1)
        self.output_field.configure(font=(self.font_family, self.font_size))
        self.output_field.tag_configure("bold", font=(self.font_family, self.font_size, "bold"))

    def copy_last_response(self):
        if self.last_ai_response:
            self.clipboard_clear()
            self.clipboard_append(self.last_ai_response)
            self.update()

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Supported", "*.pdf *.txt *.docx"),
                       ("PDF files", "*.pdf"),
                       ("Text files", "*.txt"),
                       ("Word files", "*.docx")]
        )
        if file_path:
            try:
                if file_path.endswith(".pdf"):
                    self.context_attachment = extract_text_from_pdf(file_path)
                elif file_path.endswith(".docx"):
                    self.context_attachment = extract_text_from_docx(file_path)
                elif file_path.endswith(".txt"):
                    self.context_attachment = extract_text_from_txt(file_path)

                filename = file_path.split("/")[-1]
                self.output_field.insert(tk.END, f"[Attached file: {filename}]\n", "bold")
                self.output_field.see(tk.END)

            except Exception as e:
                print(f"Failed to read file: {e}")

    def send_request(self):
        input_text = self.input_field.get().strip()
        if not input_text:
            return

        self.input_field.delete(0, tk.END)
        self.chat_history.append(f"User: {input_text}")

        prompt = ""
        if self.context_attachment:
            prompt += f"[Context from attached file]\n{self.context_attachment.strip()}\n\n"

        prompt += "\n".join(self.chat_history) + "\nAssistant:"

        self.output_field.insert(tk.END, "You: ", "bold")
        self.output_field.insert(tk.END, input_text + "\nAI: ", "bold")
        self.output_field.see(tk.END)

        threading.Thread(target=self.stream_response, args=(prompt,), daemon=True).start()

    def stream_response(self, prompt):
        assistant_reply = ""
        try:
            with requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": prompt,
                    "stream": True
                },
                stream=True
            ) as response:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            token = chunk.get("response", "")
                            assistant_reply += token
                            self.output_field.after(0, self.output_field.insert, tk.END, token)
                            self.output_field.after(0, self.output_field.see, tk.END)
                        except Exception as parse_err:
                            print(f"Parse error: {parse_err}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.last_ai_response = assistant_reply
            self.chat_history.append(f"Assistant: {assistant_reply}")
            self.output_field.after(0, self.output_field.insert, tk.END, "\n\n")

    def export_chat(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for line in self.chat_history:
                        f.write(line + "\n\n")
            except Exception as e:
                print(f"Export failed: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()