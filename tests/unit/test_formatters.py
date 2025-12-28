"""
Тесты для утилит форматирования
"""

from unittest.mock import Mock

import pytest

from models.category import Category
from models.transaction import Transaction
from utils.formatting import (
    format_categories,
    format_transactions,
)


class TestFormatters:
    """Тесты утилит форматирования"""

    def test_format_transactions_empty(self):
        """Тест форматирования пустого списка транзакций"""
        result = format_transactions([])
        assert "Транзакции не найдены" in result

    def test_format_transactions_basic(self):
        """Тест базового форматирования транзакций"""
        transactions = [
            Transaction(
                id="1", date="2025-01-15", income=0, outcome=1000, payee="Магазин"
            )
        ]

        result = format_transactions(transactions)
        assert "Найдено транзакций: 1" in result
        assert "Магазин" in result

    def test_format_transactions_with_ids(self):
        """Тест форматирования транзакций с ID"""
        transactions = [
            Transaction(
                id="test_id", date="2025-01-15", income=1000, outcome=0, payee="Доход"
            )
        ]

        result = format_transactions(transactions, show_ids=True)
        assert "test_id" in result
        assert "Доход" in result

    def test_format_categories_basic(self):
        """Тест форматирования категорий"""
        categories = {
            "cat1": Category(id="cat1", title="Продукты"),
            "cat2": Category(id="cat2", title="Транспорт"),
        }

        result = format_categories(categories)
        assert "Продукты" in result
        assert "Транспорт" in result

    def test_format_spending_report_basic(self):
        """Тест форматирования отчета по тратам"""
        data = {
            "total": 5000,
            "by_category": {"Продукты": 3000, "Транспорт": 2000},
            "period": "2025",
        }

        result = format_spending_report(data)
        assert "Продукты" in result
        assert "Транспорт" in result
        assert "3,000" in result
        assert "2,000" in result
