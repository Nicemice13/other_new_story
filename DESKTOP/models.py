from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Contact:
    """Модель данных для контакта/визитки"""
    name: str
    phones: List[str]
    email: str
    address: str
    description: str
    image_path: Optional[str] = None
    image_data: Optional[bytes] = None
    id: Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        """Создает объект Contact из словаря"""
        return cls(
            name=data.get("name", ""),
            phones=data.get("phones", []),
            email=data.get("email", ""),
            address=data.get("address", ""),
            description=data.get("description", "")
        )