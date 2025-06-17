import httpx
import asyncio
import json
import os
from dotenv import load_dotenv
import uuid
import urllib3

# Отключение предупреждений о небезопасных запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загрузка переменных окружения
load_dotenv()

# API ключ
API_KEY = os.getenv("GIGACHAT_API_KEY", "YWM3YjczZjgtNTg3Ny00NWRhLWE1MTctYWJhYzAyYjY1NTM4OjZhMjgwYTgzLTI2ZmEtNGFiZC04NTJlLWViMGZmNGU4Y2IwMw==")
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
API_URL = "https://gigachat.devices.sberbank.ru/api/v1"

async def test_simple_request():
    # Шаг 1: Получение токена
    rq_uid = str(uuid.uuid4())
    auth_headers = {
        "Authorization": f"Basic {API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid
    }
    
    print(f"1. Получение токена с RqUID: {rq_uid}")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            auth_response = await client.post(
                AUTH_URL,
                headers=auth_headers,
                data="scope=GIGACHAT_API_PERS",
                timeout=30.0
            )
            
            print(f"Статус ответа аутентификации: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                access_token = auth_data.get("access_token")
                print(f"Токен получен: {access_token[:10]}...")
                
                # Шаг 2: Отправка простого запроса
                api_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
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
                
                print("\n2. Отправка простого запроса к API...")
                print(f"URL: {API_URL}/chat/completions")
                print(f"Заголовки: {api_headers}")
                print(f"Payload: {json.dumps(payload)}")
                
                api_response = await client.post(
                    f"{API_URL}/chat/completions",
                    headers=api_headers,
                    json=payload,
                    timeout=60.0
                )
                
                print(f"\nСтатус ответа API: {api_response.status_code}")
                print(f"Заголовки ответа: {api_response.headers}")
                print(f"Тело ответа: {api_response.text[:500]}...")
                
            else:
                print(f"Ошибка аутентификации: {auth_response.status_code} - {auth_response.text}")
            
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple_request())