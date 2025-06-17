import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import logging
import urllib3
import uuid

# Отключение предупреждений о небезопасных запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Визитка Сканер")

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Получение API ключа из переменных окружения
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY", "YWM3YjczZjgtNTg3Ny00NWRhLWE1MTctYWJhYzAyYjY1NTM4OjZhMjgwYTgzLTI2ZmEtNGFiZC04NTJlLWViMGZmNGU4Y2IwMw==")
GIGACHAT_API_URL = os.getenv("GIGACHAT_API_URL", "https://gigachat.devices.sberbank.ru/api/v1")
GIGACHAT_AUTH_URL = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan", response_class=HTMLResponse)
async def scan_business_card(request: Request, file: UploadFile = File(...)):
    # Чтение загруженного изображения
    logger.info(f"Получен файл: {file.filename}, content_type: {file.content_type}")
    image_content = await file.read()
    
    if not image_content:
        logger.error("Пустой файл")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Загруженный файл пуст"}
        )

    # Проверка и преобразование изображения
    try:
        img = Image.open(BytesIO(image_content))
        logger.info(f"Изображение открыто: формат={img.format}, размер={img.size}")

        # Преобразование изображения в base64
        buffered = BytesIO()
        img.save(buffered, format=img.format if img.format else "JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        logger.info(f"Изображение преобразовано в base64, длина: {len(img_base64)}")

        # Получение токена авторизации
        # Генерация уникального RqUID
        rq_uid = str(uuid.uuid4())
        
        auth_headers = {
            "Authorization": f"Basic {GIGACHAT_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": rq_uid
        }
        
        logger.info(f"Получение токена авторизации с RqUID: {rq_uid}")
        
        try:
            async with httpx.AsyncClient(verify=False) as client:
                auth_response = await client.post(
                    GIGACHAT_AUTH_URL,
                    headers=auth_headers,
                    data="scope=GIGACHAT_API_PERS",
                    timeout=30.0
                )
                
                logger.info(f"Ответ аутентификации: статус={auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    access_token = auth_data.get("access_token")
                    logger.info("Токен авторизации получен успешно")
                    
                    # Формирование запроса к GigaChat API с полученным токеном
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    
                    # Логирование для отладки
                    logger.info("Формирование payload для запроса")
                    
                    # Формат запроса для GigaChat API
                    payload = {
                        "model": "GigaChat",
                        "messages": [
                            {
                                "role": "user",
                                "content": "Привет! Как дела?"
                            }
                        ]
                    }
                    
                    # Вывод payload для отладки
                    import json
                    logger.info(f"Payload: {json.dumps(payload)}")

                    logger.info(f"Отправка запроса к API: {GIGACHAT_API_URL}/chat/completions")
                    
                    # Отправка запроса к GigaChat API
                    # Преобразуем payload в строку JSON вручную
                    payload_json = json.dumps(payload)
                    logger.info(f"JSON строка: {payload_json}")
                    
                    async with httpx.AsyncClient(verify=False) as client:
                        response = await client.post(
                            f"{GIGACHAT_API_URL}/chat/completions",
                            headers=headers,
                            content=payload_json,
                            timeout=60.0
                        )
                        
                        logger.info(f"Получен ответ от API: статус={response.status_code}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            logger.info("Успешно получен ответ от API")
                            extracted_info = result["choices"][0]["message"]["content"]
                            return templates.TemplateResponse(
                                "result.html",
                                {"request": request, "result": extracted_info}
                            )
                        else:
                            logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                            return templates.TemplateResponse(
                                "error.html",
                                {"request": request, "error": f"Ошибка API: {response.status_code} - {response.text}"}
                            )
                else:
                    logger.error(f"Ошибка получения токена: {auth_response.status_code} - {auth_response.text}")
                    return templates.TemplateResponse(
                        "error.html",
                        {"request": request, "error": f"Ошибка получения токена: {auth_response.status_code} - {auth_response.text}"}
                    )
        except Exception as e:
            logger.error(f"Ошибка при получении токена: {str(e)}")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": f"Ошибка при получении токена: {str(e)}"}
            )

    except Exception as e:
        logger.error(f"Ошибка обработки изображения: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Ошибка обработки: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)