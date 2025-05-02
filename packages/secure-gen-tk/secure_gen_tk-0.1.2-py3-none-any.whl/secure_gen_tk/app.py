import tkinter as tk
from tkinter import messagebox
import random
import string
import pyperclip
from tkinter import font

# Функция для генерации пароля
def generate_password(length, include_digits, include_special):
    characters = string.ascii_letters  # буквы
    if include_digits:
        characters += string.digits  # цифры
    if include_special:
        characters += string.punctuation  # спецсимволы
    
    # Генерация случайного пароля
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# Функция для обновления пароля в GUI
def update_password():
    length = int(length_entry.get())
    include_digits = digits_var.get()
    include_special = special_var.get()
    
    # Генерация пароля
    password = generate_password(length, include_digits, include_special)
    
    # Обновляем текст в поле пароля
    password_var.set(password)

# Функция для копирования пароля в буфер обмена
def copy_to_clipboard():
    pyperclip.copy(password_var.get())
    messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")

# Создание главного окна
root = tk.Tk()
root.title("Secure Gen Tk - Генератор паролей")
root.geometry("450x500")
root.resizable(False, False)

# Задаём фон и цвета
root.config(bg="#f2f2f2")

# Шрифты
title_font = font.Font(family="Arial", size=18, weight="bold")
label_font = font.Font(family="Arial", size=12)
password_font = font.Font(family="Arial", size=14, weight="bold")

# Переменная для отображения пароля
password_var = tk.StringVar()

# Создание виджетов
title_label = tk.Label(root, text="Генератор паролей", font=title_font, bg="#f2f2f2", fg="#333")
title_label.pack(pady=20)

password_label = tk.Label(root, textvariable=password_var, font=password_font, bg="#ffffff", fg="#333", width=30, height=2, relief="solid", borderwidth=2, anchor="center")
password_label.pack(pady=20)

# Поле для ввода длины пароля
length_label = tk.Label(root, text="Длина пароля:", font=label_font, bg="#f2f2f2", fg="#333")
length_label.pack()

length_entry = tk.Entry(root, font=label_font, width=10, borderwidth=2, relief="solid", justify="center")
length_entry.insert(0, "12")  # Значение по умолчанию
length_entry.pack(pady=5)

# Опции для включения цифр и спецсимволов
digits_var = tk.BooleanVar()
special_var = tk.BooleanVar()

digits_checkbox = tk.Checkbutton(root, text="Включить цифры", variable=digits_var, font=label_font, bg="#f2f2f2", fg="#333")
digits_checkbox.pack()

special_checkbox = tk.Checkbutton(root, text="Включить спецсимволы", variable=special_var, font=label_font, bg="#f2f2f2", fg="#333")
special_checkbox.pack()

# Кнопки
generate_button = tk.Button(root, text="Сгенерировать пароль", command=update_password, font=label_font, bg="#4CAF50", fg="white", width=20, height=2, relief="flat", activebackground="#45a049")
generate_button.pack(pady=10)

copy_button = tk.Button(root, text="Копировать в буфер обмена", command=copy_to_clipboard, font=label_font, bg="#2196F3", fg="white", width=20, height=2, relief="flat", activebackground="#1976D2")
copy_button.pack(pady=10)

# Запуск основного цикла приложения
root.mainloop()
