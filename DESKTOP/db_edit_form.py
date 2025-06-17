import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import CRUD
from models import Contact
from PIL import Image, ImageTk
import os
import shutil

class DBEditForm:
    """Форма для редактирования визиток в базе данных"""
    def __init__(self, root):
        self.root = root
        self.contacts = []
        self.current_contact = None
        self.photo = None  # Для хранения ссылки на изображение
        
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
        
        # Кнопки управления списком
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Обновить", command=self.load_contacts).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Удалить", command=self.delete_contact).pack(
            side=tk.RIGHT, padx=2, fill=tk.X, expand=True)
        
        # Фрейм для деталей контакта
        self.details_frame = ttk.LabelFrame(details_frame, text="Редактирование визитки", padding="10")
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля для редактирования деталей
        ttk.Label(self.details_frame, text="Название компании:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(self.details_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Телефоны (через запятую):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.phones_entry = ttk.Entry(self.details_frame, width=40)
        self.phones_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(self.details_frame, width=40)
        self.email_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Адрес:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.address_entry = ttk.Entry(self.details_frame, width=40)
        self.address_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.details_frame, text="Описание:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.description_text = scrolledtext.ScrolledText(self.details_frame, width=40, height=10)
        self.description_text.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Фрейм для изображения
        image_frame = ttk.LabelFrame(details_frame, text="Изображение", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка для выбора изображения
        ttk.Button(image_frame, text="Выбрать изображение", command=self.select_image).pack(pady=5)
        
        # Кнопка сохранения
        ttk.Button(details_frame, text="Сохранить изменения", command=self.save_changes).pack(
            pady=10, fill=tk.X)
        
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
        """Отображает детали выбранного контакта для редактирования"""
        if not self.current_contact:
            return
            
        # Обновляем поля ввода
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.current_contact.name or "")
        
        self.phones_entry.delete(0, tk.END)
        self.phones_entry.insert(0, ", ".join(self.current_contact.phones) if self.current_contact.phones else "")
        
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, self.current_contact.email or "")
        
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, self.current_contact.address or "")
        
        # Обновляем текстовое поле описания
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, self.current_contact.description or "")
        
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
                    self.photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=self.photo)
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {str(e)}")
    
    def select_image(self):
        """Выбор нового изображения для контакта"""
        if not self.current_contact:
            messagebox.showinfo("Информация", "Сначала выберите контакт для редактирования")
            return
            
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")
            ]
        )
        
        if file_path:
            try:
                # Создаем директорию для изображений, если она не существует
                image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                
                # Копируем изображение в папку images
                import datetime
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.current_contact.name or 'contact'}_{now}.jpg"
                new_path = os.path.join(image_dir, filename)
                
                shutil.copy2(file_path, new_path)
                
                # Обновляем путь к изображению в текущем контакте
                self.current_contact.image_path = new_path
                
                # Отображаем новое изображение
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def save_changes(self):
        """Сохраняет изменения в контакте"""
        if not self.current_contact:
            messagebox.showinfo("Информация", "Нет выбранного контакта для сохранения")
            return
            
        try:
            # Получаем данные из полей ввода
            name = self.name_entry.get().strip()
            phones = [phone.strip() for phone in self.phones_entry.get().split(",") if phone.strip()]
            email = self.email_entry.get().strip()
            address = self.address_entry.get().strip()
            description = self.description_text.get("1.0", tk.END).strip()
            
            # Обновляем данные контакта
            self.current_contact.name = name
            self.current_contact.phones = phones
            self.current_contact.email = email
            self.current_contact.address = address
            self.current_contact.description = description
            
            # Сохраняем в базу данных
            CRUD.update_contact(self.current_contact)
            
            messagebox.showinfo("Успех", "Изменения сохранены")
            
            # Обновляем список контактов
            self.load_contacts()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {str(e)}")
    
    def delete_contact(self):
        """Удаляет выбранный контакт"""
        if not self.current_contact:
            messagebox.showinfo("Информация", "Нет выбранного контакта для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить контакт {self.current_contact.name}?"):
            try:
                CRUD.delete_contact(self.current_contact.id)
                messagebox.showinfo("Успех", "Контакт удален")
                self.load_contacts()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить контакт: {str(e)}")