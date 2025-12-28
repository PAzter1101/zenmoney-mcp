"""
Базовые фикстуры для тестов
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from models.transaction import Transaction


@pytest.fixture
def sample_expense_transaction():
    """Фикстура расходной транзакции"""
    return Transaction(
        id="exp_1",
        date="2025-01-15",
        income=0,
        outcome=1000,
        category="food",
        payee="Магазин"
    )


@pytest.fixture
def sample_income_transaction():
    """Фикстура доходной транзакции"""
    return Transaction(
        id="inc_1",
        date="2025-01-15",
        income=50000,
        outcome=0,
        category="salary",
        payee="Работодатель"
    )


@pytest.fixture
def sample_categories():
    """Фикстура категорий"""
    return {
        "food": Mock(title="Продукты"),
        "salary": Mock(title="Зарплата"),
        "transport": Mock(title="Транспорт")
    }


@pytest.fixture
def sample_accounts():
    """Фикстура счетов"""
    return {
        "acc1": Mock(title="Основной счет", balance=50000, type="cash"),
        "acc2": Mock(title="Карта", balance=25000, type="ccard")
    }


@pytest.fixture
def test_token():
    """Фикстура тестового токена"""
    return "test_token_12345"
