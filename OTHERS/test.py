import httpx
import asyncio
import uuid

async def test_auth():
    # Генерация уникального RqUID
    rq_uid = str(uuid.uuid4())
    
    # API ключ
    api_key = "YWM3YjczZjgtNTg3Ny00NWRhLWE1MTctYWJhYzAyYjY1NTM4OjZhMjgwYTgzLTI2ZmEtNGFiZC04NTJlLWViMGZmNGU4Y2IwMw=="
    
    # Заголовки запроса
    headers = {
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
            response = await client.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers=headers,
                data=data,
                timeout=30.0
            )
            
            print(f"Статус ответа: {response.status_code}")
            print(f"Заголовки ответа: {response.headers}")
            print(f"Тело ответа: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"Токен получен: {token_data.get('access_token')[:10]}...")
            
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")

# Запуск асинхронной функции
if __name__ == "__main__":
    # Отключение предупреждений о небезопасных запросах
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    asyncio.run(test_auth())