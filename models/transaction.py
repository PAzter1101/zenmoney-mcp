"""
Модели транзакций
"""

from pydantic import BaseModel
from typing import Optional, List

class Transaction(BaseModel):
    """Модель транзакции ДзенМани"""
    
    id: str
    date: str
    income: Optional[float] = 0
    outcome: Optional[float] = 0
    account: Optional[str] = None
    category: Optional[str] = None
    payee: Optional[str] = None
    comment: Optional[str] = None
    
    @property
    def amount(self) -> float:
        """Сумма транзакции (положительная для доходов, отрицательная для расходов)"""
        return self.income - self.outcome
    
    @property
    def is_expense(self) -> bool:
        """Является ли транзакция расходом"""
        return self.outcome > 0

class TransactionFilter(BaseModel):
    """Фильтр для транзакций"""
    
    year: Optional[int] = None
    month: Optional[int] = None
    category_ids: Optional[List[str]] = None
    uncategorized_only: bool = False
