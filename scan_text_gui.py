import os
import uuid
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
from PIL import Image, ImageTk
import threading
import json
import re
import psycopg2
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Параметры подключения к БД
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "card_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.runnables import RunnableConfig

load_dotenv(find_dotenv())

def recognize_text_from_image(image_path):
    model = GigaChat(
        model="GigaChat-2-Max",
        verify_ssl_certs=False,
    )

    # Загружаем изображение
    with open(image_path, "rb") as image_file:
        file_uploaded_id = model.upload_file(image_file).id_

    # Создаем конфигурацию
    config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

    # Отправляем запрос на распознавание текста
    message = {
        "role": "user",
        "content":'''
Распознай текст с этого изображения. Найди в нем название комании(name), телефоны(phones), email, адреса и сохрани их в формат json строки
{
  "name": "",
  "phones": [],
  "email": "",
  "address": "",
  "description": ""
}
''',
        "attachments": [file_uploaded_id]
    }

    response = model.invoke(
        [message],
        config=config
    )

    return response.content

class TextRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание текста с изображений")
        self.root.geometry("800x600")

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10, fill=tk.X)

        # Кнопка выбора файла
        self.select_button = tk.Button(button_frame, text="Выбрать изображение", command=self.select_image)
        self.select_button.pack(side=tk.LEFT, padx=10)

        # Кнопка распознавания
        self.recognize_button = tk.Button(button_frame, text="Распознать текст", command=self.start_recognition, state=tk.DISABLED)
        self.recognize_button.pack(side=tk.LEFT, padx=10)

        # Индикатор загрузки
        self.progress = ttk.Progressbar(button_frame, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Создаем фрейм для изображения и текста
        content_frame = tk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для изображения
        image_frame = tk.LabelFrame(content_frame, text="Изображение")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Метка для отображения изображения
        self.image_label = tk.Label(image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Фрейм для распознанного текста
        text_frame = tk.LabelFrame(content_frame, text="Распознанный текст")
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Текстовое поле для вывода распознанного текста
        self.text_output = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Переменные для хранения пути к изображению и распознанного текста
        self.image_path = None
        self.photo = None  # Для хранения ссылки на изображение (чтобы не удалялось сборщиком мусора)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def select_image(self):
        """Выбор изображения через диалоговое окно"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        if file_path:
            self.image_path = file_path
            self.status_var.set(f"Выбрано изображение: {os.path.basename(file_path)}")
            self.recognize_button.config(state=tk.NORMAL)
            self.display_image(file_path)

    def display_image(self, image_path):
        """Отображение выбранного изображения"""
        try:
            # Открываем изображение
            img = Image.open(image_path)

            # Изменяем размер для отображения
            img.thumbnail((350, 350))

            # Конвертируем в формат для tkinter
            self.photo = ImageTk.PhotoImage(img)

            # Отображаем изображение
            self.image_label.config(image=self.photo)
        except Exception as e:
            self.status_var.set(f"Ошибка при загрузке изображения: {str(e)}")

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
            recognized_text = recognize_text_from_image(self.image_path)

            # Обновляем UI в основном потоке
            self.root.after(0, self.update_ui, recognized_text)
        except Exception as e:
            # Обрабатываем ошибки
            self.root.after(0, self.handle_error, str(e))

    def update_ui(self, text):
        """Обновление UI после распознавания"""
        self.text_output.insert(tk.END, text)
        self.progress.stop()
        self.select_button.config(state=tk.NORMAL)
        self.recognize_button.config(state=tk.NORMAL)
        self.status_var.set("Распознавание завершено")
        
        # Сохраняем распознанный текст
        self.recognized_text = text
        
        # Создаем фрейм для кнопок сохранения
        if hasattr(self, 'save_frame'):
            self.save_frame.destroy()
        
        self.save_frame = tk.Frame(self.root)
        self.save_frame.pack(pady=5)
        
        # Добавляем кнопки сохранения
        save_json_button = tk.Button(self.save_frame, text="Сохранить в JSON", command=lambda: self.save_to_json(text))
        save_json_button.pack(side=tk.LEFT, padx=5)
        
        save_db_button = tk.Button(self.save_frame, text="Сохранить в БД", command=lambda: self.save_to_db(text))
        save_db_button.pack(side=tk.LEFT, padx=5)
        
    def extract_data(self, text):
        """Извлечение данных из распознанного текста"""
        try:
            # Пытаемся извлечь JSON из текста
            json_match = re.search(r'({[\s\S]*})', text)
            
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # Проверяем наличие необходимых полей
                if "name" not in data or not data["name"]:
                    return None, "Ошибка: не найдено название компании"
                
                return data, None
            else:
                # Если JSON не найден, создаем пустой шаблон
                data = {
                    "name": "",
                    "phones": [],
                    "email": "",
                    "address": "",
                    "description": text  # Помещаем весь текст в описание
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
            # Формируем имя файла из названия компании
            company_name = data["name"].strip() if data["name"] else "contact_data"
            filename = re.sub(r'[\\/*?:"<>|]', "_", company_name)  # Заменяем недопустимые символы
            
            # Сохраняем в JSON файл
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.status_var.set(f"Данные сохранены в файл: {filename}.json")
            
            if error:  # Если было предупреждение, но не критическая ошибка
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
            # Подключение к БД
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            
            # Создание курсора
            cur = conn.cursor()
            
            # Подготовка данных
            name = data.get("name", "")
            phones = data.get("phones", [])
            email = data.get("email", "")
            address = data.get("address", "")
            description = data.get("description", "")
            
            # SQL-запрос для вставки данных
            insert_query = """
            INSERT INTO contacts (name, phones, email, address, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            # Выполнение запроса
            cur.execute(insert_query, (name, phones, email, address, description))
            
            # Получение ID вставленной записи
            contact_id = cur.fetchone()[0]
            
            # Фиксация изменений
            conn.commit()
            
            # Закрытие курсора и соединения
            cur.close()
            conn.close()
            
            self.status_var.set(f"Данные сохранены в БД (ID: {contact_id})")
            messagebox.showinfo("Успех", f"Данные успешно сохранены в базу данных (ID: {contact_id})")
            
            if error:  # Если было предупреждение, но не критическая ошибка
                messagebox.showwarning("Предупреждение", error)
        except Exception as e:
            self.status_var.set(f"Ошибка при сохранении в БД: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные в БД: {str(e)}")

    def handle_error(self, error_message):
        """Обработка ошибок распознавания"""
        self.text_output.insert(tk.END, f"Ошибка при распознавании: {error_message}")
        self.progress.stop()
        self.select_button.config(state=tk.NORMAL)
        self.recognize_button.config(state=tk.NORMAL)
        self.status_var.set("Произошла ошибка")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextRecognizerApp(root)
    root.mainloop()