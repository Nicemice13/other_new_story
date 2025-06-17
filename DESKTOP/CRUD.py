import psycopg2
from database import get_connection
from models import Contact

def create_contact(contact):
    """Создает новый контакт в базе данных"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        insert_query = """
        INSERT INTO contacts (name, phones, email, address, description, image_path, image_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        cur.execute(insert_query, (
            contact.name,
            contact.phones,
            contact.email,
            contact.address,
            contact.description,
            contact.image_path,
            psycopg2.Binary(contact.image_data) if contact.image_data else None
        ))
        contact_id = cur.fetchone()[0]
        conn.commit()
        return contact_id
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def get_contact(contact_id):
    """Получает контакт по ID"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, phones, email, address, description, image_path FROM contacts WHERE id = %s", (contact_id,))
        row = cur.fetchone()
        if row:
            return Contact(
                id=row[0],
                name=row[1],
                phones=row[2],
                email=row[3],
                address=row[4],
                description=row[5],
                image_path=row[6]
            )
        return None
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def update_contact(contact):
    """Обновляет существующий контакт"""
    if not contact.id:
        return False
        
    conn = get_connection()
    try:
        cur = conn.cursor()
        update_query = """
        UPDATE contacts 
        SET name = %s, phones = %s, email = %s, address = %s, 
            description = %s, image_path = %s
        WHERE id = %s;
        """
        cur.execute(update_query, (
            contact.name,
            contact.phones,
            contact.email,
            contact.address,
            contact.description,
            contact.image_path,
            contact.id
        ))
        conn.commit()
        return True
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def get_all_contacts():
    """Получает все контакты из базы данных"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, phones, email, address, description, image_path FROM contacts ORDER BY name")
        rows = cur.fetchall()
        return [
            Contact(
                id=row[0],
                name=row[1],
                phones=row[2],
                email=row[3],
                address=row[4],
                description=row[5],
                image_path=row[6]
            )
            for row in rows
        ]
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def delete_contact(contact_id):
    """Удаляет контакт по ID"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
        conn.commit()
        return True
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()