# 🗂️ Contact Extractor — Сервис извлечения контактных данных

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/opencv-4.x-5C3EE8.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![Tesseract OCR](https://img.shields.io/badge/tesseract-5.x-FF6600.svg)](https://github.com/tesseract-ocr/tesseract)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Backend-сервис для автоматического извлечения контактной информации из изображений с использованием компьютерного зрения

---

## 🎯 Проблема и решение

**Бизнес-проблема:**
Ручной ввод контактных данных из изображений — трудоёмкий процесс, подверженный ошибкам и не масштабируемый при работе с большим количеством информации.

**Техническое решение:**
Сервис автоматизирует полный цикл обработки:
1. Приём изображения (JPG/PNG)
2. Предварительная обработка для улучшения качества
3. Распознавание текста через OCR-движок
4. Структурирование данных (ФИО, компания, телефон, email)
5. Сохранение в локальное хранилище контактов

---

## ⚙️ Технологический стек

```python
# Ядро обработки
- OpenCV (cv2)      — предобработка изображений, улучшение контраста
- Tesseract OCR     — распознавание текста (поддержка русского/английского)
- Pillow (PIL)      — работа с форматами изображений
- NumPy             — математические операции с пикселями

# Хранение данных
- SQLite            — локальное хранилище структурированных контактов

# Интерфейс
- argparse          — CLI для автоматизации и интеграции в пайплайны

🚀 Быстрый старт
Установка зависимостей

# Создание виртуального окружения (рекомендуется)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Клонирование репозитория
git clone https://github.com/Nicemice13/contact-extractor.git
cd contact-extractor

# Установка библиотек
pip install -r requirements.txt

# Для Linux/macOS: установка Tesseract
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS

# Для Windows: скачать установщик с официального сайта
# https://github.com/UB-Mannheim/tesseract/wiki

Запуск сервиса

# Обработка одного изображения
python main.py --image path/to/image.jpg

# Пакетная обработка из папки
python main.py --folder path/to/images_folder/

# Просмотр сохранённых контактов
python main.py --list-contacts


🖼️ Примеры работы
Входные данные → Результат
## 🖼️ Пример работы системы
## 🖼️ Пример работы системы

Конвейер извлечения структурированных данных из изображения визитки:

| Шаг | Описание | Результат |
|-----|----------|-----------|
| **1. Исходное изображение** | Загрузка фото/скана визитки | 📷 ![Визитка Pappalporto](https://via.placeholder.com/300x150/ffffff/000000?text=Pappalporto+Visiting+Card) |
| **2. Предобработка** | Улучшение контраста, удаление шума, бинаризация | 🖼️ ![Обработанное изображение](https://via.placeholder.com/300x150/ffffff/000000?text=Processed+Image) |
| **3. Распознавание текста (OCR)** | Извлечение «сырого» текста | `PAPPALPORTO • Giorgia e Papà • Via del Porto, 37 - 61011 Gabicce Mare (PU) • 340.9891290 • pappalporto@gmail.com` |
| **4. Структурирование данных** | Парсинг в поля сущности | ```json
{
  "company": "PAPPALPORTO",
  "owners": "Giorgia e Papà",
  "address": "Via del Porto, 37 - 61011 Gabicce Mare (PU)",
  "phone": "340.9891290",
  "email": "pappalporto@gmail.com"
}
``` |

> 💡 **Примечание**:
> В реальном проекте:
> - Для итальянских номеров телефонов добавляется префикс `+39`
> - Адрес автоматически разбивается на компоненты (улица, индекс, город)
> - Поле `owners` может быть заменено на `contact_person` при наличии персональных данных