"""
Отчет по тратам
"""

from collections import defaultdict
from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient
from utils.filtering import filter_transactions, get_transaction_category_name

from .base import BaseReport


class SpendingReport(BaseReport):
    """Отчет по тратам за период"""

    async def generate(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Генерация отчета по тратам"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()

        filter_params = self._create_filter_params(args)
        filtered = filter_transactions(transactions, filter_params)

        # Разделение на переводы и расходы
        expenses = [t for t in filtered if t.is_expense(filtered)]

        if not expenses:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="📊 Расходы за период не найдены")
                ]
            )

        total_expenses = sum(t.outcome or 0.0 for t in expenses if t.outcome)
        by_category: Dict[str, float] = defaultdict(float)

        for t in expenses:
            cat_name = get_transaction_category_name(t, categories)
            by_category[cat_name] += t.outcome or 0.0

        period_desc = self._get_period_description(args)
        result = f"📊 Отчет по тратам за {period_desc}\n\n"
        result += f"Общие траты: {total_expenses:,.2f} ₽\n"
        result += f"Количество транзакций: {len(expenses)}\n"
        result += f"Средняя трата: {total_expenses / len(expenses):,.2f} ₽\n\n"

        if by_category:
            result += "По категориям:\n"
            for cat_name, amount in by_category.items():
                result += f"  {cat_name}: {amount:,.2f} ₽\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
