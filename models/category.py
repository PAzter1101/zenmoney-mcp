"""
Модели категорий
"""

from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    """Модель категории ДзенМани"""
    
    id: str
    title: str
    parent: Optional[str] = None
    
    @property
    def is_parent(self) -> bool:
        """Является ли категория родительской"""
        return self.parent is None
