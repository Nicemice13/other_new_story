import os
import re
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
from PIL import Image, ImageTk
import threading
import shutil
from models import Contact
from AI import recognize_text_from_file
import CRUD

class TextRecognizerApp:
    """Приложение для распознавания текста с изображений и визиток"""
    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание текста с изображений")
        self.root.geometry("800x600")
        
        # Инициализация переменных
        self.image_path = None
        self.photo = None
        self.recognized_text = None

        # Создаем главное меню
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # Создаем пункты меню
        self.main_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Меню", menu=self.main_menu)

        # Добавляем команды в меню
        self.main_menu.add_command(label="Сканировать и распознать", command=self.show_scan_frame)
        self.main_menu.add_command(label="Просмотр визиток", command=self.show_view_cards)
        self.main_menu.add_command(label="Редактирование визиток", command=self.show_edit_cards)
        self.main_menu.add_separator()
        self.main_menu.add_command(label="Выход", command=root.quit)

        # Создаем основной интерфейс
        self.setup_scan_interface()
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_scan_interface(self):
        """Настройка интерфейса сканирования"""
        # Фрейм для содержимого
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(pady=10, fill=tk.X)

        # Кнопки
        self.select_button = tk.Button(button_frame, text="Выбрать изображение", command=self.select_image)
        self.select_button.pack(side=tk.LEFT, padx=10)

        self.recognize_button = tk.Button(button_frame, text="Распознать текст", 
                                         command=self.start_recognition, state=tk.DISABLED)
        self.recognize_button.pack(side=tk.LEFT, padx=10)

        # Индикатор загрузки
        self.progress = ttk.Progressbar(button_frame, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Фрейм для изображения и текста
        inner_content_frame = tk.Frame(self.content_frame)
        inner_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для изображения
        image_frame = tk.LabelFrame(inner_content_frame, text="Изображение")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Метка для отображения изображения
        self.image_label = tk.Label(image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Фрейм для распознанного текста
        text_frame = tk.LabelFrame(inner_content_frame, text="Распознанный текст")
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Текстовое поле для вывода распознанного текста
        self.text_output = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_image(self):
        """Выбор изображения или PDF через диалоговое окно"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение или PDF",
            filetypes=[
                ("Все поддерживаемые форматы", "*.png *.jpg *.jpeg *.bmp *.gif *.pdf"),
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PDF файлы", "*.pdf")
            ]
        )

        if file_path:
            self.image_path = file_path
            self.status_var.set(f"Выбран файл: {os.path.basename(file_path)}")
            self.recognize_button.config(state=tk.NORMAL)

            # Отображаем изображение или иконку PDF
            if file_path.lower().endswith('.pdf'):
                self.display_pdf_icon()
            else:
                self.display_image(file_path)

    def display_image(self, image_path):
        """Отображение выбранного изображения"""
        try:
            img = Image.open(image_path)
            img.thumbnail((350, 350))
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo)
        except Exception as e:
            self.status_var.set(f"Ошибка при загрузке изображения: {str(e)}")

    def display_pdf_icon(self):
        """Отображение иконки PDF"""
        try:
            pdf_icon = tk.Canvas(self.image_label, width=100, height=120, bg="white")
            pdf_icon.create_rectangle(10, 10, 90, 110, outline="red", width=2)
            pdf_icon.create_text(50, 40, text="PDF", font=("Arial", 24), fill="red")
            pdf_icon.create_text(50, 70, text="Документ", font=("Arial", 10))
            self.image_label.config(image="")
            pdf_icon.pack(expand=True)
            self.pdf_icon = pdf_icon
        except Exception as e:
            self.status_var.set(f"Ошибка при отображении иконки PDF: {str(e)}")

    def start_recognition(self):
        """Запуск распознавания в отдельном потоке"""
        if not self.image_path:
            self.status_var.set("Сначала выберите изображение")
            return

        # Блокируем кнопки и показываем прогресс
        self.select_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Распознавание текста...")
        self.text_output.delete(1.0, tk.END)

        # Запускаем распознавание в отдельном потоке
        threading.Thread(target=self.recognize_text, daemon=True).start()

    def recognize_text(self):
        """Распознавание текста в отдельном потоке"""
        try:
            recognized_text = recognize_text_from_file(self.image_path)
            self.root.after(0, self.update_ui, recognized_text)
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))

    def update_ui(self, text):
        """Обновление UI после распознавания"""
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        self.progress.stop()
        self.select_button.config(state=tk.NORMAL)
        self.recognize_button.config(state=tk.NORMAL)
        self.status_var.set("Распознавание завершено")
        self.recognized_text = text

        # Создаем фрейм для кнопок сохранения
        if hasattr(self, 'save_frame'):
            self.save_frame.destroy()

        self.save_frame = tk.Frame(self.root)
        self.save_frame.pack(pady=5)

        # Кнопки сохранения
        save_json_button = tk.Button(self.save_frame, text="Сохранить в JSON", 
                                    command=lambda: self.save_to_json(text))
        save_json_button.pack(side=tk.LEFT, padx=5)

        save_db_button = tk.Button(self.save_frame, text="Сохранить в БД", 
                                  command=lambda: self.save_to_db(text))
        save_db_button.pack(side=tk.LEFT, padx=5)

    def extract_data(self, text):
        """Извлечение данных из распознанного текста"""
        try:
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                if "name" not in data or not data["name"]:
                    return None, "Ошибка: не найдено название компании"
                return data, None
            else:
                data = {
                    "name": "",
                    "phones": [],
                    "email": "",
                    "address": "",
                    "description": text
                }
                return data, "Предупреждение: JSON не найден в тексте"
        except Exception as e:
            return None, f"Ошибка при извлечении данных: {str(e)}"

    def save_to_json(self, text):
        """Сохранение распознанного текста в JSON файл"""
        data, error = self.extract_data(text)
        if error and not data:
            self.status_var.set(error)
            return

        try:
            company_name = data["name"].strip() if data["name"] else "contact_data"
            filename = re.sub(r'[\\/*?:"<>|]', "_", company_name)
            
            cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
            if not os.path.exists(cards_dir):
                os.makedirs(cards_dir)
                
            file_path = os.path.join(cards_dir, f"{filename}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.status_var.set(f"Данные сохранены в файл: {filename}.json")
            if error:
                messagebox.showwarning("Предупреждение", error)
        except Exception as e:
            self.status_var.set(f"Ошибка при сохранении: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def save_to_db(self, text):
        """Сохранение распознанного текста в базу данных"""
        data, error = self.extract_data(text)
        if error and not data:
            self.status_var.set(error)
            return

        try:
            # Сохраняем изображение
            image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

            import datetime
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            company_name = data.get("name", "").strip() if data.get("name") else "contact"
            company_name = re.sub(r'[\\/*?:"<>|]', "_", company_name)
            
            image_filename = f"{company_name}_{now}.jpg"
            image_path = os.path.join(image_dir, image_filename)
            shutil.copy2(self.image_path, image_path)

            # Читаем изображение в бинарном формате
            with open(self.image_path, 'rb') as img_file:
                binary_data = img_file.read()

            # Создаем объект контакта
            contact = Contact(
                name=data.get("name", ""),
                phones=data.get("phones", []),
                email=data.get("email", ""),
                address=data.get("address", ""),
                description=data.get("description", ""),
                image_path=image_path,
                image_data=binary_data
            )

            # Сохраняем в БД
            contact_id = CRUD.create_contact(contact)
            self.status_var.set(f"Данные сохранены в БД (ID: {contact_id})")
            messagebox.showinfo("Успех", f"Данные успешно сохранены в базу данных (ID: {contact_id})")

            if error:
                messagebox.showwarning("Предупреждение", error)
        except Exception as e:
            self.status_var.set(f"Ошибка при сохранении в БД: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные в БД: {str(e)}")

    def handle_error(self, error_message):
        """Обработка ошибок распознавания"""
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, f"Ошибка при распознавании: {error_message}")
        self.progress.stop()
        self.select_button.config(state=tk.NORMAL)
        self.recognize_button.config(state=tk.NORMAL)
        self.status_var.set("Произошла ошибка")
        print(f"Ошибка распознавания: {error_message}")

    def show_scan_frame(self):
        """Показать интерфейс сканирования и распознавания"""
        self.hide_all_frames()
        if hasattr(self, 'content_frame'):
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_var.set("Режим сканирования и распознавания")

    def show_view_cards(self):
        """Показать интерфейс просмотра визиток"""
        self.hide_all_frames()
        if not hasattr(self, 'view_frame'):
            self.create_view_frame()
        self.update_cards_list()
        self.view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_var.set("Режим просмотра визиток")

    def create_view_frame(self):
        """Создание фрейма для просмотра визиток"""
        self.view_frame = tk.Frame(self.root)
        tk.Label(self.view_frame, text="Просмотр сохраненных визиток", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        list_frame = tk.Frame(self.view_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cards_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.cards_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.cards_listbox.yview)
        
        view_button = tk.Button(self.view_frame, text="Просмотреть", command=self.view_selected_card)
        view_button.pack(pady=10)

    def show_edit_cards(self):
        """Показать интерфейс редактирования визиток"""
        self.hide_all_frames()
        if not hasattr(self, 'edit_frame'):
            self.create_edit_frame()
        self.update_edit_cards_list()
        self.edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_var.set("Режим редактирования визиток")

    def create_edit_frame(self):
        """Создание фрейма для редактирования визиток"""
        self.edit_frame = tk.Frame(self.root)
        tk.Label(self.edit_frame, text="Редактирование визиток", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        list_frame = tk.Frame(self.edit_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.edit_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.edit_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.edit_listbox.yview)
        
        button_frame = tk.Frame(self.edit_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        edit_button = tk.Button(button_frame, text="Редактировать", command=self.edit_selected_card)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Удалить", command=self.delete_selected_card)
        delete_button.pack(side=tk.LEFT, padx=5)

    def hide_all_frames(self):
        """Скрыть все фреймы интерфейса"""
        frames = ['content_frame', 'view_frame', 'edit_frame', 'save_frame']
        for frame_name in frames:
            if hasattr(self, frame_name):
                getattr(self, frame_name).pack_forget()

    def update_cards_list(self):
        """Обновить список визиток для просмотра"""
        self.cards_listbox.delete(0, tk.END)
        cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
        if os.path.exists(cards_dir):
            card_files = [f for f in os.listdir(cards_dir) if f.endswith('.json')]
            for card_file in sorted(card_files):
                try:
                    with open(os.path.join(cards_dir, card_file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        company_name = data.get("name", "Без названия")
                    self.cards_listbox.insert(tk.END, f"{company_name} ({card_file})")
                except Exception:
                    self.cards_listbox.insert(tk.END, f"Ошибка чтения: {card_file}")

    def update_edit_cards_list(self):
        """Обновить список визиток для редактирования"""
        self.edit_listbox.delete(0, tk.END)
        cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
        if os.path.exists(cards_dir):
            card_files = [f for f in os.listdir(cards_dir) if f.endswith('.json')]
            for card_file in sorted(card_files):
                try:
                    with open(os.path.join(cards_dir, card_file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        company_name = data.get("name", "Без названия")
                    self.edit_listbox.insert(tk.END, f"{company_name} ({card_file})")
                except Exception:
                    self.edit_listbox.insert(tk.END, f"Ошибка чтения: {card_file}")

    def view_selected_card(self):
        """Просмотр выбранной визитки"""
        selection = self.cards_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите визитку для просмотра")
            return

        selected_item = self.cards_listbox.get(selection[0])
        file_name = selected_item.split('(')[-1].strip(')')
        cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
        file_path = os.path.join(cards_dir, file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.show_card_details(data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def show_card_details(self, data):
        """Показать детали визитки"""
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Просмотр визитки: {data.get('name', 'Без названия')}")
        view_window.geometry("500x400")

        # Отображаем данные
        tk.Label(view_window, text="Название компании:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Label(view_window, text=data.get("name", ""), font=("Arial", 12)).grid(
            row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(view_window, text="Телефоны:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        phones_text = ", ".join(data.get("phones", [])) if data.get("phones") else ""
        tk.Label(view_window, text=phones_text, font=("Arial", 12)).grid(
            row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(view_window, text="Email:", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Label(view_window, text=data.get("email", ""), font=("Arial", 12)).grid(
            row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(view_window, text="Адрес:", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=5)
        tk.Label(view_window, text=data.get("address", ""), font=("Arial", 12)).grid(
            row=3, column=1, sticky="w", padx=10, pady=5)

        tk.Label(view_window, text="Описание:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky="nw", padx=10, pady=5)

        desc_text = scrolledtext.ScrolledText(view_window, wrap=tk.WORD, width=40, height=10)
        desc_text.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        desc_text.insert(tk.END, data.get("description", ""))
        desc_text.config(state=tk.DISABLED)

        tk.Button(view_window, text="Закрыть", command=view_window.destroy).grid(
            row=5, column=0, columnspan=2, pady=10)

    def edit_selected_card(self):
        """Редактирование выбранной визитки"""
        selection = self.edit_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите визитку для редактирования")
            return

        selected_item = self.edit_listbox.get(selection[0])
        file_name = selected_item.split('(')[-1].strip(')')
        cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
        file_path = os.path.join(cards_dir, file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.show_edit_form(data, file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def show_edit_form(self, data, file_path):
        """Показать форму редактирования"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование визитки: {data.get('name', 'Без названия')}")
        edit_window.geometry("500x450")

        # Поля для редактирования
        tk.Label(edit_window, text="Название компании:", font=("Arial", 12)).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        name_entry = tk.Entry(edit_window, width=40, font=("Arial", 12))
        name_entry.insert(0, data.get("name", ""))
        name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(edit_window, text="Телефоны (через запятую):", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        phones_entry = tk.Entry(edit_window, width=40, font=("Arial", 12))
        phones_entry.insert(0, ", ".join(data.get("phones", [])) if data.get("phones") else "")
        phones_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(edit_window, text="Email:", font=("Arial", 12)).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        email_entry = tk.Entry(edit_window, width=40, font=("Arial", 12))
        email_entry.insert(0, data.get("email", ""))
        email_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(edit_window, text="Адрес:", font=("Arial", 12)).grid(
            row=3, column=0, sticky="w", padx=10, pady=5)
        address_entry = tk.Entry(edit_window, width=40, font=("Arial", 12))
        address_entry.insert(0, data.get("address", ""))
        address_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        tk.Label(edit_window, text="Описание:", font=("Arial", 12)).grid(
            row=4, column=0, sticky="nw", padx=10, pady=5)
        desc_text = scrolledtext.ScrolledText(edit_window, wrap=tk.WORD, width=40, height=10)
        desc_text.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        desc_text.insert(tk.END, data.get("description", ""))

        # Функция сохранения изменений
        def save_changes():
            try:
                updated_data = {
                    "name": name_entry.get().strip(),
                    "phones": [phone.strip() for phone in phones_entry.get().split(",") if phone.strip()],
                    "email": email_entry.get().strip(),
                    "address": address_entry.get().strip(),
                    "description": desc_text.get("1.0", tk.END).strip()
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, ensure_ascii=False, indent=2)

                messagebox.showinfo("Успех", "Изменения сохранены")
                edit_window.destroy()
                self.update_cards_list()
                self.update_edit_cards_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {str(e)}")

        # Кнопки
        button_frame = tk.Frame(edit_window)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Сохранить", command=save_changes).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=edit_window.destroy).pack(side=tk.LEFT, padx=10)

    def delete_selected_card(self):
        """Удаление выбранной визитки"""
        selection = self.edit_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите визитку для удаления")
            return

        selected_item = self.edit_listbox.get(selection[0])
        file_name = selected_item.split('(')[-1].strip(')')

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить визитку {file_name}?"):
            try:
                cards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")
                file_path = os.path.join(cards_dir, file_name)
                os.remove(file_path)
                messagebox.showinfo("Успех", "Визитка удалена")
                self.update_cards_list()
                self.update_edit_cards_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл: {str(e)}")