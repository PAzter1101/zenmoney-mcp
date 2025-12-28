"""
Утилиты фильтрации данных
"""

from typing import List

from models.transaction import Transaction, TransactionFilter


def filter_transactions(
    transactions: List[Transaction], filter_params: TransactionFilter
) -> List[Transaction]:
    """Фильтрация транзакций по параметрам"""
    result = transactions

    # Фильтрация по диапазону дат (приоритет)
    if filter_params.date_from or filter_params.date_to:
        if filter_params.date_from and filter_params.date_to:
            result = [
                t
                for t in result
                if filter_params.date_from <= t.date <= filter_params.date_to
            ]
        elif filter_params.date_from:
            result = [t for t in result if t.date >= filter_params.date_from]
        elif filter_params.date_to:
            result = [t for t in result if t.date <= filter_params.date_to]
    else:
        # Фильтрация по году/месяцу/дню (старая логика)
        if filter_params.year:
            year_str = str(filter_params.year)
            if filter_params.month:
                if filter_params.day:
                    date_str = (
                        f"{year_str}-{filter_params.month:02d}-{filter_params.day:02d}"
                    )
                    result = [t for t in result if t.date == date_str]
                else:
                    month_str = f"{year_str}-{filter_params.month:02d}"
                    result = [t for t in result if t.date.startswith(month_str)]
            else:
                result = [t for t in result if t.date.startswith(year_str)]

    if filter_params.uncategorized_only:
        result = [t for t in result if not t.category]

    if filter_params.category_ids:
        result = [t for t in result if t.category in filter_params.category_ids]

    return result


def find_duplicates(transactions: List[Transaction]) -> List[List[Transaction]]:
    """Поиск возможных дублей транзакций"""
    duplicates = []
    processed = set()

    for i, t1 in enumerate(transactions):
        if i in processed:
            continue

        group = [t1]
        for j, t2 in enumerate(transactions[i + 1 :], i + 1):
            if (
                t1.date == t2.date
                and abs(t1.amount - t2.amount) < 0.01
                and t1.payee == t2.payee
            ):
                group.append(t2)
                processed.add(j)

        if len(group) > 1:
            duplicates.append(group)

    return duplicates
