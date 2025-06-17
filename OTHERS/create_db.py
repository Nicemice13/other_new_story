import psycopg2
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Параметры подключения к БД
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "card_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def create_table():
    """Создание таблицы контактов в БД"""
    # SQL-запрос для создания таблицы
    create_table_query = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phones TEXT[],
        email VARCHAR(255),
        address TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    conn = None
    try:
        # Подключение к БД
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Создание курсора
        cur = conn.cursor()
        
        # Выполнение запроса
        cur.execute(create_table_query)
        
        # Фиксация изменений
        conn.commit()
        
        print("Таблица contacts успешно создана")
        
        # Закрытие курсора
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при создании таблицы: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_table()