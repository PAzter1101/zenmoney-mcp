"""
Тесты для моделей данных
"""

import pytest

from models.account import Account
from models.category import Category


class TestAccountModel:
    """Тесты модели счета"""

    def test_account_creation(self):
        """Тест создания счета"""
        account = Account(id="acc1", title="Основной счет", balance=50000, type="cash")

        assert account.id == "acc1"
        assert account.title == "Основной счет"
        assert account.balance == 50000
        assert account.type == "cash"

    def test_account_string_representation(self):
        """Тест строкового представления счета"""
        account = Account(id="acc1", title="Карта", balance=25000, type="ccard")

        str_repr = str(account)
        assert "acc1" in str_repr
        assert "Карта" in str_repr


class TestCategoryModel:
    """Тесты модели категории"""

    def test_category_creation(self):
        """Тест создания категории"""
        category = Category(id="cat1", title="Продукты")

        assert category.id == "cat1"
        assert category.title == "Продукты"

    def test_category_with_parent(self):
        """Тест категории с родителем"""
        category = Category(id="cat2", title="Хлеб", parent="cat1")

        assert category.id == "cat2"
        assert category.title == "Хлеб"
        assert category.parent == "cat1"

    def test_category_with_parent_check(self):
        """Тест проверки родительской категории"""
        # Категория без родителя
        parent_category = Category(id="cat1", title="Продукты")
        assert parent_category.parent is None

        # Категория с родителем
        child_category = Category(id="cat2", title="Хлеб", parent="cat1")
        assert child_category.parent == "cat1"
