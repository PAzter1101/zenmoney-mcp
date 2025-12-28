"""
Получение транзакций
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filtering import filter_transactions, get_transaction_category_name
from utils.formatting import format_transactions

from .base import BaseDataTool


class TransactionsTool(BaseDataTool):
    """Получение транзакций с фильтрацией"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение транзакций"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()

        # Фильтрация по дате
        filter_params = TransactionFilter(
            year=args.get("year"),
            month=args.get("month"),
            day=args.get("day"),
            date_from=args.get("date_from"),
            date_to=args.get("date_to"),
        )

        filtered = filter_transactions(transactions, filter_params)

        # Фильтрация по получателю
        payee = args.get("payee")
        if payee:
            payee_lower = payee.lower()
            filtered = [
                t for t in filtered if t.payee and payee_lower in t.payee.lower()
            ]

        # Фильтрация по категориям
        categories_filter = args.get("category")
        if categories_filter:
            category_ids = set()
            category_names = set()

            for category in categories_filter:
                if category in categories:
                    # Это ID категории
                    category_ids.add(category)
                    category_names.add(categories[category].title)
                else:
                    # Ищем по названию категории
                    category_lower = category.lower()
                    found = False
                    for cat_id, cat_obj in categories.items():
                        if cat_obj.title.lower() == category_lower:
                            category_ids.add(cat_id)
                            category_names.add(cat_obj.title)
                            found = True
                            break

                    # Если не найдено среди категорий, добавляем как название
                    if not found:
                        category_names.add(category)

            # Применяем фильтр используя ту же логику, что и в отчетах
            filtered = [
                t
                for t in filtered
                if get_transaction_category_name(t, categories) in category_names
            ]

        limit = args.get("limit", 50)
        filtered = filtered[:limit]

        show_ids = args.get("show_ids", False)
        result = format_transactions(filtered, show_ids=show_ids)
        return CallToolResult(content=[TextContent(type="text", text=result)])
