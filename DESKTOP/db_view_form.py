import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import CRUD
from PIL import Image, ImageTk
import os

class DBViewForm:
    """Форма для просмотра визиток из базы данных"""
    def __init__(self, root):
        self.root = root
        self.contacts = []
        self.current_contact = None
        
        # Создание фреймов
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Разделение на две части: список и детали
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Список контактов
        ttk.Label(list_frame, text="Список визиток", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.contacts_listbox = tk.Listbox(list_frame, width=30, font=("Arial", 10))
        self.contacts_listbox.pack(fill=tk.BOTH, expand=True)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.on_contact_select)
        
        # Кнопка обновления списка
        ttk.Button(list_frame, text="Обновить список", command=self.load_contacts).pack(pady=10, fill=tk.X)
        
        # Фрейм для деталей контакта
        self.details_frame = ttk.LabelFrame(details_frame, text="Детали визитки", padding="10")
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля для отображения деталей
        ttk.Label(self.details_frame, text="Название компании:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Label(self.details_frame, textvariable=self.name_var, font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Телефоны:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.phones_var = tk.StringVar()
        ttk.Label(self.details_frame, textvariable=self.phones_var).grid(
            row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Label(self.details_frame, textvariable=self.email_var).grid(
            row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Адрес:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        ttk.Label(self.details_frame, textvariable=self.address_var).grid(
            row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Описание:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.description_text = scrolledtext.ScrolledText(self.details_frame, width=40, height=10)
        self.description_text.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.description_text.config(state=tk.DISABLED)
        
        # Фрейм для изображения
        image_frame = ttk.LabelFrame(details_frame, text="Изображение", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Загрузка контактов
        self.load_contacts()
    
    def load_contacts(self):
        """Загружает контакты из базы данных"""
        try:
            self.contacts = CRUD.get_all_contacts()
            self.contacts_listbox.delete(0, tk.END)
            
            for contact in self.contacts:
                self.contacts_listbox.insert(tk.END, contact.name or "Без названия")
                
            if self.contacts:
                self.contacts_listbox.selection_set(0)
                self.on_contact_select(None)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить контакты: {str(e)}")
    
    def on_contact_select(self, event):
        """Обработчик выбора контакта из списка"""
        selection = self.contacts_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if 0 <= index < len(self.contacts):
            self.current_contact = self.contacts[index]
            self.display_contact_details()
    
    def display_contact_details(self):
        """Отображает детали выбранного контакта"""
        if not self.current_contact:
            return
            
        # Обновляем текстовые поля
        self.name_var.set(self.current_contact.name or "")
        self.phones_var.set(", ".join(self.current_contact.phones) if self.current_contact.phones else "")
        self.email_var.set(self.current_contact.email or "")
        self.address_var.set(self.current_contact.address or "")
        
        # Обновляем текстовое поле описания
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, self.current_contact.description or "")
        self.description_text.config(state=tk.DISABLED)
        
        # Отображаем изображение, если оно есть
        self.display_image()
    
    def display_image(self):
        """Отображает изображение контакта, если оно есть"""
        self.image_label.config(image="")
        
        if self.current_contact and self.current_contact.image_path:
            try:
                if os.path.exists(self.current_contact.image_path):
                    img = Image.open(self.current_contact.image_path)
                    img.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo  # Сохраняем ссылку
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {str(e)}")