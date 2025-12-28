"""
Простые тесты для основных компонентов
"""

from datetime import datetime

import pytest

from models.transaction import Transaction
from utils.validators import validate_date_format, validate_period_params


class TestTransactionModel:
    """Дополнительные тесты для модели транзакции"""

    def test_transaction_amount_calculation(self):
        """Тест расчета суммы транзакции"""
        # Доходная транзакция
        income_tx = Transaction(
            id="1", date="2025-01-15", income=1000, outcome=0, payee="Доход"
        )
        assert income_tx.amount == 1000

        # Расходная транзакция
        expense_tx = Transaction(
            id="2", date="2025-01-15", income=0, outcome=500, payee="Расход"
        )
        assert expense_tx.amount == -500

    def test_transaction_type_detection(self):
        """Тест определения типа транзакции"""
        # Доход
        income_tx = Transaction(id="1", date="2025-01-15", income=1000, outcome=0)
        assert income_tx.is_income is True
        assert income_tx.is_expense is False

        # Расход
        expense_tx = Transaction(id="2", date="2025-01-15", income=0, outcome=500)
        assert expense_tx.is_income is False
        assert expense_tx.is_expense is True

    def test_transaction_with_none_values(self):
        """Тест транзакции с None значениями"""
        tx = Transaction(id="1", date="2025-01-15", income=None, outcome=1000)
        assert tx.amount == -1000
        assert tx.is_expense is True


class TestValidators:
    """Дополнительные тесты валидаторов"""

    def test_date_format_edge_cases(self):
        """Тест граничных случаев валидации дат"""
        # Валидные даты
        assert validate_date_format("2025-01-01") is True
        assert validate_date_format("2025-12-31") is True

        # Невалидные даты (простая проверка формата, не семантики)
        assert validate_date_format("15-01-2025") is False
        assert validate_date_format("") is False
        assert validate_date_format("not-a-date") is False

    def test_period_validation_edge_cases(self):
        """Тест граничных случаев валидации периодов"""
        # Граничные валидные значения
        errors = validate_period_params(year=2000, month=1)
        assert len(errors) == 0

        errors = validate_period_params(year=2030, month=12)
        assert len(errors) == 0

        # Граничные невалидные значения
        errors = validate_period_params(year=1999)
        assert len(errors) == 1

        errors = validate_period_params(year=2031)
        assert len(errors) == 1


class TestBasicFunctionality:
    """Тесты базового функционала без внешних зависимостей"""

    def test_transaction_creation_with_minimal_data(self):
        """Тест создания транзакции с минимальными данными"""
        tx = Transaction(id="test_id", date="2025-01-15")
        assert tx.id == "test_id"
        assert tx.date == "2025-01-15"
        # По умолчанию income и outcome равны 0, а не None
        assert tx.income == 0
        assert tx.outcome == 0

    def test_transaction_string_representation(self):
        """Тест строкового представления транзакции"""
        tx = Transaction(
            id="1", date="2025-01-15", income=0, outcome=1000, payee="Магазин"
        )
        # Проверяем, что строковое представление содержит основную информацию
        str_repr = str(tx)
        assert "1" in str_repr
        assert "2025-01-15" in str_repr
