"""
Отчет по категориям
"""

from collections import defaultdict
from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions

from .base import BaseReport


class CategoryBreakdownReport(BaseReport):
    """Разбивка трат по категориям"""

    async def generate(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Генерация отчета по категориям"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()

        filter_params = TransactionFilter(
            year=args.get("year"), month=args.get("month")
        )

        filtered = filter_transactions(transactions, filter_params)

        by_category: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"count": 0, "income": 0, "outcome": 0}
        )

        for t in filtered:
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title

            by_category[cat_name]["count"] += 1

            # Используем правильную логику для доходов и расходов
            if hasattr(t, "is_income") and t.is_income:
                by_category[cat_name]["income"] += t.income or 0.0
            elif t.is_expense(filtered) is True:
                by_category[cat_name]["outcome"] += t.outcome or 0.0

        result = f"📊 Разбивка по категориям за {args['year']}"
        if args.get("month"):
            result += f"-{args['month']:02d}"
        result += "\n\n"

        sorted_cats = sorted(
            by_category.items(), key=lambda x: x[1]["outcome"], reverse=True
        )

        for cat_name, data in sorted_cats:
            if data["count"] > 0:  # Показываем только категории с транзакциями
                result += f"{cat_name}:\n"
                result += f"  Транзакций: {data['count']}\n"
                if data["income"] > 0:
                    result += f"  Доходы: +{data['income']:,.2f} ₽\n"
                if data["outcome"] > 0:
                    result += f"  Расходы: -{data['outcome']:,.2f} ₽\n"
                result += f"  Баланс: {data['income'] - data['outcome']:+,.2f} ₽\n\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
