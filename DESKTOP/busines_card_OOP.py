
# класс Деятельность(коды ОКВЭД, укрупненно все разделы)
# класс Компания(название компании,деятельность компании, телефон, адрес фактический, электронная почта)
# класс Визитка(наследование от Компании, название визтки,год выпуска,теги, ссылка на скан изображения)
# класс Менеджер визиток(список визиток, CRUD, поиск по тегам, сортировка)

from typing import List, Optional

class Activity:
    def __init__(self, code: str, name: str):
        self.code: str = code
        self.name: str = name


class Company:
    def __init__(self, name: str, activity: Activity, phone: str, address: str, email: str):
        self.name: str = name
        self.activity: Activity = activity
        self.phone: str = phone
        self.address: str = address
        self.email: str = email

class VisitCard:
    def __init__(self, company: Company, year: str, tags: List[str], image_path: str):
        self.company: Company = company
        self.year: str = year
        self.tags: List[str] = tags
        self.image_path: str = image_path

class VisitCardManager:
    def __init__(self):
        self.visit_cards = []

    def add_visit_card(self, visit_card):
        self.visit_cards.append(visit_card)

    def search_by_tag(self, tag):
        return [card for card in self.visit_cards if tag in card.tags]

    def sort_by_year(self):
        return sorted(self.visit_cards, key=lambda x: x.year)

    def delete_visit_card(self, visit_card):
        self.visit_cards.remove(visit_card)


        
# Возьми ОКВЭД раздела А и вставь в класс Деятельность
a = Activity( "А", "Аграрно-сельскохозяйственное культурное производство")
b = Activity("Б", "Добыча полезных ископаемых")
company_c1 = Company("Компания 1", a, "1234567890", "Адрес 1", "email1@example.com")
company_c2 = Company("Компания 2", b, "0987654321", "Адрес 2", "email2@example.com")
v1 = VisitCard("Визитка 1", "2023", ["тег1", "тег2"], "image1.jpg")
v2 = VisitCard("Визитка 2", "2022", ["тег2", "тег3"], "image2.jpg")
manager = VisitCardManager()
manager.add_visit_card(company_c1)
manager.add_visit_card(company_c2)
