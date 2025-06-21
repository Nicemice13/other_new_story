# класс Деятельность(коды ОКВЭД, укрупненно все разделы)
# класс Компания(название компании,деятельность компании, телефон, адрес фактический, электронная почта)
# класс Визитка(наследование от Компании, название визтки,год выпуска,теги, ссылка на скан изображения)
# класс Менеджер визиток(список визиток, CRUD, поиск по тегам, сортировка)

import json
import os
from typing import List, Optional, Dict

class Activity:
    def __init__(self, code: str, name: str):
        self.code: str = code
        self.name: str = name

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def __repr__(self) -> str:
        return f"Activity(code='{self.code}', name='{self.name}')"


class Company:
    def __init__(self, name: str, activities: List[Activity], phone: str, address: str, email: str):
        self.name: str = name
        self.activities: List[Activity] = activities
        self.phone: str = phone
        self.address: str = address
        self.email: str = email

    def __str__(self) -> str:
        codes = [activity.code for activity in self.activities]
        return f"{self.name} ({', '.join(codes)})"
        
    def add_activity(self, activity: Activity):
        """Добавление вида деятельности"""
        self.activities.append(activity)


class VisitCard:
    def __init__(self, company: Company, year: str, tags: List[str], image_path: str):
        self.company: Company = company
        self.year: str = year
        self.tags: List[str] = tags
        self.image_path: str = image_path

    def __str__(self) -> str:
        return f"Визитка {self.company.name} ({self.year})"


class VisitCardManager:
    def __init__(self):
        self.visit_cards: List[VisitCard] = []
        self.activities: Dict[str, Activity] = {}
        self.load_activities()

    def load_activities(self):
        """Загрузка кодов ОКВЭД из JSON-файла"""
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'okved_data.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                activities_data = json.load(f)

            for item in activities_data:
                activity = Activity(item['code'], item['name'])
                self.activities[item['code']] = activity

            print(f"Загружено {len(self.activities)} кодов ОКВЭД")
        except Exception as e:
            print(f"Ошибка при загрузке кодов ОКВЭД: {e}")
            # Создаем минимальный набор кодов ОКВЭД
            self.activities = {
                "A": Activity("A", "Сельское, лесное хозяйство, охота, рыболовство и рыбоводство"),
                "B": Activity("B", "Добыча полезных ископаемых"),
                "C": Activity("C", "Обрабатывающие производства"),
                "D": Activity("D", "Обеспечение электрической энергией, газом и паром"),
                "E": Activity("E", "Водоснабжение; водоотведение, организация сбора и утилизации отходов"),
                "F": Activity("F", "Строительство"),
                "G": Activity("G", "Торговля оптовая и розничная"),
                "H": Activity("H", "Транспортировка и хранение"),
                "I": Activity("I", "Деятельность гостиниц и предприятий общественного питания"),
                "J": Activity("J", "Деятельность в области информации и связи")
            }

    def get_activity(self, code: str) -> Optional[Activity]:
        """Получение деятельности по коду ОКВЭД"""
        return self.activities.get(code)

    def get_activities_by_section(self, section_code: str) -> List[Activity]:
        """Получение всех видов деятельности по коду раздела"""
        return [activity for code, activity in self.activities.items()
                if code.startswith(section_code)]

    def add_visit_card(self, visit_card: VisitCard):
        """Добавление визитки в список"""
        self.visit_cards.append(visit_card)

    def search_by_tag(self, tag: str) -> List[VisitCard]:
        """Поиск визиток по тегу"""
        return [card for card in self.visit_cards if tag in card.tags]

    def search_by_activity(self, activity_code: str) -> List[VisitCard]:
        """Поиск визиток по коду деятельности"""
        return [card for card in self.visit_cards
                if any(activity.code.startswith(activity_code) for activity in card.company.activities)]

    def sort_by_year(self) -> List[VisitCard]:
        """Сортировка визиток по году"""
        return sorted(self.visit_cards, key=lambda x: x.year)

    def delete_visit_card(self, visit_card: VisitCard):
        """Удаление визитки из списка"""
        self.visit_cards.remove(visit_card)


# Пример использования
if __name__ == "__main__":
    # Создаем менеджер визиток
    manager = VisitCardManager()

    # Получаем деятельность по коду
    activity_a = manager.get_activity("A")
    activity_j = manager.get_activity("J")

    if activity_a and activity_j:
        # Создаем компании
        company1 = Company("Агрофирма Заря", [activity_a], "+7 (123) 456-78-90",
                          "г. Москва, ул. Полевая, 1", "info@zarya.ru")

        # Компания с несколькими видами деятельности
        activity_c = manager.get_activity("C")
        company2 = Company("IT Solutions", [activity_j, activity_c], "+7 (987) 654-32-10",
                          "г. Санкт-Петербург, пр. Невский, 100", "contact@itsolutions.com")

        # Создаем визитки
        card1 = VisitCard(company1, "2023", ["сельское хозяйство", "растениеводство"], "images/card1.jpg")
        card2 = VisitCard(company2, "2022", ["IT", "разработка ПО"], "images/card2.jpg")

        # Добавляем визитки в менеджер
        manager.add_visit_card(card1)
        manager.add_visit_card(card2)

        # Выводим информацию о визитках
        print("\nСписок визиток:")
        for card in manager.visit_cards:
            activities_str = ", ".join(str(activity) for activity in card.company.activities)
            print(f"- {card}: {activities_str}")

        # Поиск по тегу
        it_cards = manager.search_by_tag("IT")
        print("\nВизитки с тегом 'IT':")
        for card in it_cards:
            print(f"- {card}")

        # Поиск по коду деятельности
        agro_cards = manager.search_by_activity("A")
        print("\nВизитки с кодом деятельности 'A':")
        for card in agro_cards:
            print(f"- {card}")

        # Получение всех видов деятельности по разделу
        print("\nВиды деятельности раздела 'J':")
        j_activities = manager.get_activities_by_section("J")
        for activity in j_activities[:5]:  # Выводим первые 5 для краткости
            print(f"- {activity}")
    else:
        print("Не удалось загрузить коды ОКВЭД")