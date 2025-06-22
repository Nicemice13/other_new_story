import re
import json

def fallback_text_recognition(text):
    """
    Резервная функция для обработки текста, когда API GigaChat недоступен.
    Выполняет базовый анализ текста для извлечения информации о компании.
    
    Args:
        text (str): Текст для анализа
        
    Returns:
        str: JSON-строка с извлеченными данными
    """
    # Создаем пустой шаблон данных
    data = {
        "name": "",
        "phones": [],
        "email": "",
        "addresses": [],
        "description": text,
        "country": "Россия"
    }
    
    # Извлекаем название компании (обычно в начале текста или после "ООО", "АО", "ИП" и т.д.)
    company_patterns = [
        r"(?:ООО|АО|ПАО|ЗАО|ИП)\s+[«\"]?([^\"»\n.]{3,50})[»\"]?",
        r"^([A-ZА-Я][A-ZА-Яa-zа-я\s]{3,50}(?:LLC|ООО|АО|ПАО|ЗАО|ИП)?)"
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text)
        if company_match:
            data["name"] = company_match.group(1).strip()
            break
    
    # Извлекаем телефоны
    phone_patterns = [
        r"(?:\+7|8)[\s\(]*\d{3}[\s\)]*\d{3}[\s-]*\d{2}[\s-]*\d{2}",
        r"\+\d{1,3}\s?\(\d{1,4}\)\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}",
        r"\+\d{10,15}"
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            data["phones"].extend(phones)
    
    # Извлекаем email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        data["email"] = email_match.group(0)
    
    # Извлекаем адреса (это сложно сделать точно, используем эвристики)
    address_patterns = [
        r"(?:г\.|город)\s+[А-Яа-я\-]+[\s,]+(?:ул\.|улица)\s+[А-Яа-я\-]+[\s,]+(?:д\.|дом)\s+\d+",
        r"\d{6}[\s,]+[А-Яа-я\-]+[\s,]+[А-Яа-я\-]+[\s,]+[А-Яа-я\-]+[\s,]+\d+"
    ]
    
    for pattern in address_patterns:
        addresses = re.findall(pattern, text)
        if addresses:
            data["addresses"].extend(addresses)
    
    # Определяем страну по ключевым словам
    countries = {
        "Россия": ["россия", "рф", "москва", "санкт-петербург", "новосибирск"],
        "США": ["сша", "usa", "united states", "america"],
        "Германия": ["германия", "germany", "deutschland"],
        "Китай": ["китай", "china"],
        "Великобритания": ["великобритания", "англия", "uk", "england"]
    }
    
    text_lower = text.lower()
    for country, keywords in countries.items():
        for keyword in keywords:
            if keyword in text_lower:
                data["country"] = country
                break
        if data["country"] != "Россия":
            break
    
    # Для обратной совместимости
    if data["addresses"]:
        data["address"] = data["addresses"][0]
    else:
        data["address"] = ""
    
    # Возвращаем результат в формате JSON-строки
    return json.dumps(data, ensure_ascii=False, indent=2)

def process_image_fallback(image_path):
    """
    Резервная функция для обработки изображения, когда API GigaChat недоступен.
    Возвращает заглушку с сообщением об ошибке.
    
    Args:
        image_path (str): Путь к изображению
        
    Returns:
        str: JSON-строка с базовой информацией
    """
    data = {
        "name": "Не удалось распознать",
        "phones": [],
        "email": "",
        "addresses": [],
        "address": "",
        "description": "API GigaChat недоступен. Пожалуйста, попробуйте позже или введите данные вручную.",
        "country": "Россия"
    }
    
    return json.dumps(data, ensure_ascii=False, indent=2)