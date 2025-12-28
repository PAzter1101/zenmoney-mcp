"""
Модели счетов
"""

from pydantic import BaseModel
from typing import Optional

class Account(BaseModel):
    """Модель счета ДзенМани"""
    
    id: str
    title: str
    balance: float
    type: str
    currency: Optional[str] = "RUB"
