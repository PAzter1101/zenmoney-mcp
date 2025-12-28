"""
Утилиты форматирования вывода
"""

from typing import Any, Dict, List

from models.category import Category
from models.transaction import Transaction


def format_transactions(
    transactions: List[Transaction], limit: int = 20, show_ids: bool = False
) -> str:
    """Форматирование списка транзакций"""
    if not transactions:
        return "Транзакции не найдены"

    result = f"Найдено транзакций: {len(transactions)}\n\n"

    for i, t in enumerate(transactions[:limit], 1):
        payee = (t.payee or "Без получателя")[:25]
        amount = f"{t.amount:+.2f}"

        if show_ids:
            result += f"{i:2d}. {t.date} | {amount:>10} | {payee} | ID: {t.id}\n"
        else:
            result += f"{i:2d}. {t.date} | {amount:>10} | {payee}\n"

    if len(transactions) > limit:
        result += f"\n... и еще {len(transactions) - limit} транзакций"

    return result


def _separate_categories(
    categories: Dict[str, Category],
) -> tuple[Dict[str, Category], Dict[str, List[tuple[str, Category]]]]:
    """Разделяет категории на родительские и дочерние"""
    parent_categories: Dict[str, Category] = {}
    child_categories: Dict[str, List[tuple[str, Category]]] = {}

    for cat_id, cat in categories.items():
        if cat.parent is None:
            parent_categories[cat_id] = cat
        else:
            if cat.parent not in child_categories:
                child_categories[cat.parent] = []
            child_categories[cat.parent].append((cat_id, cat))

    return parent_categories, child_categories


def _format_parent_with_children(
    parent_id: str,
    parent_cat: Category,
    child_categories: Dict[str, List[tuple[str, Category]]],
    counter: int,
) -> tuple[str, int]:
    """Форматирует родительскую категорию с дочерними"""
    result = f"{counter:2d}. {parent_cat.title} (ID: {parent_id})\n"
    counter += 1

    if parent_id in child_categories:
        sorted_children = sorted(child_categories[parent_id], key=lambda x: x[1].title)
        for child_id, child_cat in sorted_children:
            result += f"    └─ {child_cat.title} (ID: {child_id})\n"
            counter += 1

    return result, counter


def format_categories(categories: Dict[str, Category]) -> str:
    """Форматирование списка категорий с иерархией"""
    if not categories:
        return "Категории не найдены"

    parent_categories, child_categories = _separate_categories(categories)

    result = f"Всего категорий: {len(categories)}\n"
    parent_count = len(parent_categories)
    child_count = len(categories) - parent_count
    result += f"Родительских: {parent_count}, Дочерних: {child_count}\n\n"

    # Сортируем родительские категории
    sorted_parents = sorted(parent_categories.items(), key=lambda x: x[1].title)

    counter = 1
    for parent_id, parent_cat in sorted_parents:
        parent_result, counter = _format_parent_with_children(
            parent_id, parent_cat, child_categories, counter
        )
        result += parent_result

    # Добавляем категории с отсутствующими родителями
    orphaned = [
        (cat_id, cat)
        for cat_id, cat in categories.items()
        if cat.parent is not None and cat.parent not in categories
    ]

    if orphaned:
        result += "\nКатегории с отсутствующими родителями:\n"
        for cat_id, cat in sorted(orphaned, key=lambda x: x[1].title):
            result += (
                f"{counter:2d}. {cat.title} (ID: {cat_id}) "
                f"[родитель: {cat.parent}]\n"
            )
            counter += 1

    return result


def format_spending_report(data: Dict[str, Any]) -> str:
    """Форматирование отчета по тратам"""
    total = data.get("total_expenses", 0)
    count = data.get("transaction_count", 0)
    avg = data.get("average_expense", 0)

    result = "📊 Отчет по тратам\n\n"
    result += f"Общие траты: {total:,.2f} ₽\n"
    result += f"Количество транзакций: {count}\n"
    result += f"Средняя трата: {avg:,.2f} ₽\n\n"

    if "by_category" in data:
        result += "По категориям:\n"
        for cat, amount in sorted(
            data["by_category"].items(), key=lambda x: x[1], reverse=True
        )[:10]:
            result += f"  {cat}: {amount:,.2f} ₽\n"

    return result
