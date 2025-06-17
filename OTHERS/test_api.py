import httpx
import asyncio
import uuid
import json
import base64
from io import BytesIO
from PIL import Image

async def test_api_call():
    # Генерация уникального RqUID
    rq_uid = str(uuid.uuid4())
    
    # API ключ
    api_key = "YWM3YjczZjgtNTg3Ny00NWRhLWE1MTctYWJhYzAyYjY1NTM4OjZhMjgwYTgzLTI2ZmEtNGFiZC04NTJlLWViMGZmNGU4Y2IwMw=="
    
    # Заголовки запроса для аутентификации
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid,
        "Authorization": f"Basic {api_key}"
    }
    
    # Данные запроса
    data = "scope=GIGACHAT_API_PERS"
    
    print(f"Отправка запроса на аутентификацию с RqUID: {rq_uid}")
    
    # Отправка запроса с отключенной проверкой SSL
    async with httpx.AsyncClient(verify=False) as client:
        try:
            auth_response = await client.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers=auth_headers,
                data=data,
                timeout=30.0
            )
            
            print(f"Статус ответа аутентификации: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                access_token = auth_data.get("access_token")
                print(f"Токен получен: {access_token[:10]}...")
                
                # Заголовки для запроса к API
                api_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Простой запрос без изображения для проверки
                simple_payload = {
                    "model": "GigaChat",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Привет! Как дела?"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                
                print("Отправка простого запроса к API...")
                print(f"Payload: {json.dumps(simple_payload)}")
                
                api_response = await client.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers=api_headers,
                    json=simple_payload,
                    timeout=60.0
                )
                
                print(f"Статус ответа API: {api_response.status_code}")
                print(f"Заголовки ответа: {api_response.headers}")
                print(f"Тело ответа: {api_response.text[:200]}...")
                
            else:
                print(f"Ошибка аутентификации: {auth_response.status_code} - {auth_response.text}")
            
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")

# Запуск асинхронной функции
if __name__ == "__main__":
    # Отключение предупреждений о небезопасных запросах
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    asyncio.run(test_api_call())