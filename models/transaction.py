"""
Модели транзакций
"""

from typing import List, Optional

from pydantic import BaseModel


class Transaction(BaseModel):
    """Модель транзакции ДзенМани"""

    id: str
    date: str
    income: Optional[float] = 0
    outcome: Optional[float] = 0
    account: Optional[str] = None
    incomeAccount: Optional[str] = None
    outcomeAccount: Optional[str] = None
    category: Optional[str] = None
    payee: Optional[str] = None
    comment: Optional[str] = None

    # Дополнительные поля из API
    user: Optional[int] = None
    changed: Optional[int] = None
    incomeInstrument: Optional[int] = None
    outcomeInstrument: Optional[int] = None
    created: Optional[int] = None
    originalPayee: Optional[str] = None
    deleted: Optional[bool] = None
    viewed: Optional[bool] = None
    hold: Optional[bool] = None
    qrCode: Optional[str] = None  # QR-код чека
    source: Optional[str] = None
    tag: Optional[List[str]] = None
    opIncome: Optional[float] = None
    opOutcome: Optional[float] = None
    opIncomeInstrument: Optional[int] = None
    opOutcomeInstrument: Optional[int] = None
    latitude: Optional[float] = None  # Координаты места покупки
    longitude: Optional[float] = None
    merchant: Optional[str] = None  # ID торговца
    incomeBankID: Optional[str] = None
    outcomeBankID: Optional[str] = None
    reminderMarker: Optional[str] = None

    @property
    def amount(self) -> float:
        """Сумма транзакции (положительная для доходов, отрицательная для расходов)"""
        income = self.income or 0.0
        outcome = self.outcome or 0.0
        return income - outcome

    @property
    def is_expense(self) -> bool:
        """Является ли транзакция расходом (исключая переводы между счетами)"""
        # Если нет outcome - точно не расход
        if not self.outcome or self.outcome <= 0:
            return False

        # Если incomeAccount и outcomeAccount разные - это перевод между счетами
        if (
            self.incomeAccount
            and self.outcomeAccount
            and self.incomeAccount != self.outcomeAccount
        ):
            return False

        # Если есть outcome, но нет income - это расход
        if not self.income or self.income <= 0:
            return True

        # Если есть и income и outcome на одном счете - это тоже расход
        return True

    @property
    def is_income(self) -> bool:
        """Является ли транзакция доходом (исключая переводы между счетами)"""
        # Если нет income - точно не доход
        if not self.income or self.income <= 0:
            return False

        # Если incomeAccount и outcomeAccount разные - это перевод между счетами
        if (
            self.incomeAccount
            and self.outcomeAccount
            and self.incomeAccount != self.outcomeAccount
        ):
            return False

        # Если есть income, но нет outcome - это доход
        if not self.outcome or self.outcome <= 0:
            return True

        return False

    @property
    def is_transfer(self) -> bool:
        """Является ли транзакция переводом между счетами"""
        return bool(
            self.incomeAccount
            and self.outcomeAccount
            and self.incomeAccount != self.outcomeAccount
        )

    def is_paired_with(
        self, other_transaction: "Transaction", tolerance: float = 0.01
    ) -> bool:
        """Проверяет, является ли эта транзакция парной с другой (внутренний перевод)"""
        if not other_transaction or self.id == other_transaction.id:
            return False

        # Проверяем дату (должна быть одинаковая)
        if self.date != other_transaction.date:
            return False

        # Проверяем суммы (одна должна быть доходом, другая расходом с одинаковой суммой)
        self_outcome = self.outcome or 0.0
        other_income = other_transaction.income or 0.0
        self_income = self.income or 0.0
        other_outcome = other_transaction.outcome or 0.0

        if (
            abs(self_outcome - other_income) <= tolerance
            and self_outcome > 0
            and other_income > 0
            and self_income == 0
            and other_outcome == 0
        ):
            return True

        if (
            abs(self_income - other_outcome) <= tolerance
            and self_income > 0
            and other_outcome > 0
            and self_outcome == 0
            and other_income == 0
        ):
            return True

        return False


class TransactionFilter(BaseModel):
    """Фильтр для транзакций"""

    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None  # YYYY-MM-DD
    category_ids: Optional[List[str]] = None
    uncategorized_only: bool = False
