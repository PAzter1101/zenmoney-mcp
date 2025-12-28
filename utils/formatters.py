"""
Утилиты форматирования вывода
"""

from typing import List, Dict, Any
from models.transaction import Transaction
from models.category import Category

def format_transactions(transactions: List[Transaction], limit: int = 20) -> str:
    """Форматирование списка транзакций"""
    if not transactions:
        return "Транзакции не найдены"
    
    result = f"Найдено транзакций: {len(transactions)}\n\n"
    
    for i, t in enumerate(transactions[:limit], 1):
        payee = (t.payee or 'Без получателя')[:25]
        amount = f"{t.amount:+.2f}"
        result += f"{i:2d}. {t.date} | {amount:>10} | {payee}\n"
    
    if len(transactions) > limit:
        result += f"\n... и еще {len(transactions) - limit} транзакций"
    
    return result

def format_categories(categories: Dict[str, Category]) -> str:
    """Форматирование списка категорий"""
    if not categories:
        return "Категории не найдены"
    
    result = f"Всего категорий: {len(categories)}\n\n"
    
    cat_list = [(cat.title, cat_id) for cat_id, cat in categories.items()]
    cat_list.sort()
    
    for i, (title, cat_id) in enumerate(cat_list, 1):
        result += f"{i:2d}. {title}\n"
    
    return result

def format_spending_report(data: Dict[str, Any]) -> str:
    """Форматирование отчета по тратам"""
    total = data.get('total_expenses', 0)
    count = data.get('transaction_count', 0)
    avg = data.get('average_expense', 0)
    
    result = f"📊 Отчет по тратам\n\n"
    result += f"Общие траты: {total:,.2f} ₽\n"
    result += f"Количество транзакций: {count}\n"
    result += f"Средняя трата: {avg:,.2f} ₽\n\n"
    
    if 'by_category' in data:
        result += "По категориям:\n"
        for cat, amount in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True)[:10]:
            result += f"  {cat}: {amount:,.2f} ₽\n"
    
    return result
