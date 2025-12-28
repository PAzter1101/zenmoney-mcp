"""
Отчет по тратам
"""

from collections import defaultdict
from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from utils.formatters import format_spending_report

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
        transfers = [t for t in filtered if hasattr(t, "is_transfer") and t.is_transfer]
        expenses = [t for t in filtered if hasattr(t, "is_expense") and t.is_expense]

        if not expenses:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="📊 Расходы за период не найдены")
                ]
            )

        total_expenses = sum(t.outcome or 0.0 for t in expenses if t.outcome)
        by_category: Dict[str, float] = defaultdict(float)

        for t in expenses:
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title
            by_category[cat_name] += t.outcome or 0.0

        report_data = {
            "total_expenses": total_expenses,
            "transaction_count": len(expenses),
            "average_expense": total_expenses / len(expenses) if expenses else 0,
            "by_category": dict(by_category),
        }

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
