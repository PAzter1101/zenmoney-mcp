"""
Модели счетов
"""

from typing import Optional

from pydantic import BaseModel


class Account(BaseModel):
    """Модель счета ДзенМани"""

    id: str
    title: str
    balance: float
    type: str
    currency: Optional[str] = "RUB"
