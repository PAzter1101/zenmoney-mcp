"""
Тесты для валидаторов
"""

import pytest
from utils.validators import validate_date_format, validate_period_params


class TestDateValidation:
    """Тесты валидации дат"""

    def test_valid_date_format(self):
        """Тест валидного формата даты"""
        assert validate_date_format("2025-01-15") is True

    def test_invalid_date_format(self):
        """Тест невалидного формата даты"""
        assert validate_date_format("15-01-2025") is False
        assert validate_date_format("invalid") is False


class TestPeriodValidation:
    """Тесты валидации периодов"""

    def test_valid_period_params(self):
        """Тест валидных параметров периода"""
        errors = validate_period_params(year=2025, month=1)
        assert len(errors) == 0

    def test_invalid_year(self):
        """Тест невалидного года"""
        errors = validate_period_params(year=1999)
        assert "Год должен быть в диапазоне 2000-2030" in errors

    def test_invalid_month(self):
        """Тест невалидного месяца"""
        errors = validate_period_params(year=2025, month=13)
        assert "Месяц должен быть в диапазоне 1-12" in errors
