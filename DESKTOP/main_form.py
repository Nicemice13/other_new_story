import tkinter as tk
from tkinter import ttk, messagebox
import os
from GUI import TextRecognizerApp
from db_view_form import DBViewForm
from db_edit_form import DBEditForm

class MainForm:
    """Главная форма приложения с кнопками навигации"""
    def __init__(self, root):
        self.root = root
        self.root.title("Визитки - Главное меню")
        self.root.geometry("400x300")
        
        # Настройка стиля
        self.setup_style()
        
        # Создание фрейма для содержимого
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление визитками", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Кнопки навигации
        scan_button = ttk.Button(main_frame, text="Сканирование", 
                                command=self.open_scan_form, width=30)
        scan_button.pack(pady=10)
        
        view_button = ttk.Button(main_frame, text="Просмотр БД", 
                                command=self.open_view_form, width=30)
        view_button.pack(pady=10)
        
        edit_button = ttk.Button(main_frame, text="Редактирование БД", 
                                command=self.open_edit_form, width=30)
        edit_button.pack(pady=10)
        
        # Кнопка выхода
        exit_button = ttk.Button(main_frame, text="Выход", 
                                command=root.quit, width=30)
        exit_button.pack(pady=20)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_style(self):
        """Настройка стиля для кнопок и элементов интерфейса"""
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12))
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TFrame", background="#f0f0f0")
    
    def open_scan_form(self):
        """Открывает форму сканирования"""
        self.status_var.set("Открытие формы сканирования...")
        scan_window = tk.Toplevel(self.root)
        scan_window.title("Сканирование визиток")
        scan_window.geometry("800x600")
        TextRecognizerApp(scan_window)
        self.status_var.set("Форма сканирования открыта")
    
    def open_view_form(self):
        """Открывает форму просмотра БД"""
        self.status_var.set("Открытие формы просмотра БД...")
        view_window = tk.Toplevel(self.root)
        view_window.title("Просмотр визиток из БД")
        view_window.geometry("800x600")
        DBViewForm(view_window)
        self.status_var.set("Форма просмотра БД открыта")
    
    def open_edit_form(self):
        """Открывает форму редактирования БД"""
        self.status_var.set("Открытие формы редактирования БД...")
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование визиток в БД")
        edit_window.geometry("800x600")
        DBEditForm(edit_window)
        self.status_var.set("Форма редактирования БД открыта")