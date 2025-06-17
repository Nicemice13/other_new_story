import tkinter as tk
from database import init_db
from main_form import MainForm

def main():
    """Точка входа в приложение"""
    # Инициализация базы данных
    init_db()
    
    # Создание и запуск главной формы
    root = tk.Tk()
    app = MainForm(root)
    root.mainloop()

if __name__ == "__main__":
    main()