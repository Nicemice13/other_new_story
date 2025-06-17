import os
import base64
import tempfile
import ssl
from PIL import Image
import fitz  # PyMuPDF для работы с PDF
from langchain_gigachat import GigaChat

def process_image(file_path):
    """Обрабатывает изображение, уменьшая его размер при необходимости"""
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    if file_size > 4:
        img = Image.open(file_path)
        temp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_img.name, format="JPEG", quality=50)
        temp_img.close()
        return temp_img.name
    return file_path

def process_pdf(file_path):
    """Конвертирует PDF в изображение"""
    pdf_document = fitz.open(file_path)
    if len(pdf_document) > 0:
        page = pdf_document[0]
        scale = min(0.2, 1000 / page.rect.width)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        temp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        pix.save(temp_img.name)
        temp_img.close()
        pdf_document.close()
        return temp_img.name
    pdf_document.close()
    return ""

def recognize_text_from_file(file_path):
    """Распознавание текста из файла изображения или PDF"""
    model = GigaChat(
        model="GigaChat-2-Max",
        verify_ssl_certs=False,
        auto_upload_images=True,
        timeout=120
    )

    # Обработка файла в зависимости от типа
    if file_path.lower().endswith('.pdf'):
        file_path = process_pdf(file_path)
    else:
        file_path = process_image(file_path)

    # Чтение файла и кодирование в base64
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    mime_type = "image/jpeg"

    # Формирование запроса к модели
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": '''
Распознай текст с этого изображения. Найди в нем название комании(name), телефоны(phones), email, адреса и сохрани их в формат json строки
{
  "name": "",
  "phones": [],
  "email": "",
  "address": "",
  "description": ""
}
'''
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{file_base64}"
                    }
                }
            ]
        }
    ]

    try:
        response = model.invoke(messages)
        return response.content
    except Exception as e:
        return f"Ошибка при обработке запроса: {str(e)}"