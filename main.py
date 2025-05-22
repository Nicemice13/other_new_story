import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Визитка Сканер")

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Получение API ключа из переменных окружения
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
GIGACHAT_API_URL = os.getenv("GIGACHAT_API_URL", "https://gigachat-api.ru/v1")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan", response_class=HTMLResponse)
async def scan_business_card(request: Request, file: UploadFile = File(...)):
    # Чтение загруженного изображения
    image_content = await file.read()
    
    # Проверка и преобразование изображения
    try:
        img = Image.open(BytesIO(image_content))
        
        # Преобразование изображения в base64
        buffered = BytesIO()
        img.save(buffered, format=img.format if img.format else "JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Формирование запроса к GigaChat API
        headers = {
            "Authorization": f"Bearer {GIGACHAT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - помощник для распознавания текста с визиток. Извлеки из изображения следующую информацию: ФИО, должность, компания, телефон, email, адрес. Верни результат в формате JSON."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Распознай текст с этой визитки и извлеки контактную информацию."
                        },
                        {
                            "type": "image",
                            "image": img_base64
                        }
                    ]
                }
            ]
        }
        
        # Отправка запроса к GigaChat API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GIGACHAT_API_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_info = result["choices"][0]["message"]["content"]
                return templates.TemplateResponse(
                    "result.html", 
                    {"request": request, "result": extracted_info}
                )
            else:
                return templates.TemplateResponse(
                    "error.html", 
                    {"request": request, "error": f"Ошибка API: {response.status_code} - {response.text}"}
                )
                
    except Exception as e:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": f"Ошибка обработки: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)