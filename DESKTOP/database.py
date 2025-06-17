import os
from dotenv import load_dotenv, find_dotenv
import psycopg2

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Параметры подключения к БД
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "card_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def init_db():
    """Инициализирует базу данных, создавая необходимые таблицы"""
    conn = get_connection()
    conn.close()