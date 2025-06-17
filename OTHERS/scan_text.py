import os
import uuid

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
        "content": "Распознай текст с этого изображения и выведи его полностью.",
        "attachments": [file_uploaded_id]
    }
    
    response = model.invoke(
        [message],
        config=config
    )
    
    return response.content

def main():
    # Запрашиваем путь к изображению
    image_path = input("Введите путь к изображению: ")    
    # Проверяем существование файла
    if not os.path.exists(image_path):
        print(f"Файл {image_path} не найден")
        return
    
    # Распознаем текст
    print("Распознаю текст...")
    recognized_text = recognize_text_from_image(image_path)
    
    # Выводим результат
    print("\nРаспознанный текст:")
    print("-" * 50)
    print(recognized_text)
    print("-" * 50)

if __name__ == "__main__":   
    main()
