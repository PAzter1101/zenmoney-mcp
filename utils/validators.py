"""
Утилиты валидации данных
"""

from typing import Dict, Any, List
import re

def validate_date_format(date_str: str) -> bool:
    """Проверка формата даты YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def validate_transaction_data(data: Dict[str, Any]) -> List[str]:
    """Валидация данных транзакции"""
    errors = []
    
    if not data.get('id'):
        errors.append("Отсутствует ID транзакции")
    
    if not data.get('date') or not validate_date_format(data['date']):
        errors.append("Некорректная дата транзакции")
    
    income = data.get('income', 0)
    outcome = data.get('outcome', 0)
    
    if income < 0 or outcome < 0:
        errors.append("Суммы не могут быть отрицательными")
    
    if income > 0 and outcome > 0:
        errors.append("Транзакция не может быть одновременно доходом и расходом")
    
    if income == 0 and outcome == 0:
        errors.append("Сумма транзакции не может быть нулевой")
    
    return errors

def validate_period_params(year: int = None, month: int = None) -> List[str]:
    """Валидация параметров периода"""
    errors = []
    
    if year and (year < 2000 or year > 2030):
        errors.append("Год должен быть в диапазоне 2000-2030")
    
    if month and (month < 1 or month > 12):
        errors.append("Месяц должен быть в диапазоне 1-12")
    
    return errors
