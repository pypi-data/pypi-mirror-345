import tkinter as tk
from tkinter import messagebox
from . import generator

def generate_password():
    mode = mode_var.get()
    try:
        if mode == "Simple":
            length = int(entry.get())
            result = generator.simple_password(length)
        elif mode == "Secure":
            length = int(entry.get())
            result = generator.secure_password(length)
        elif mode == "Memorable":
            num_words = int(entry.get())
            result = generator.memorable_password(num_words)
        elif mode == "Passphrase":
            num_words = int(entry.get())
            result = generator.passphrase(num_words)
        else:
            result = "Выберите режим."
        result_label.config(text=result)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

root = tk.Tk()
root.title("Secure Gen TK")

tk.Label(root, text="Режим:").pack()

mode_var = tk.StringVar(value="Simple")
modes = ["Simple", "Secure", "Memorable", "Passphrase"]
for m in modes:
    tk.Radiobutton(root, text=m, variable=mode_var, value=m).pack(anchor=tk.W)

tk.Label(root, text="Длина / Кол-во слов:").pack()
entry = tk.Entry(root)
entry.insert(0, "8")
entry.pack()

tk.Button(root, text="Сгенерировать", command=generate_password).pack(pady=5)
result_label = tk.Label(root, text="", fg="blue", wraplength=300)
result_label.pack(pady=10)

def start_app():
    root.mainloop()
