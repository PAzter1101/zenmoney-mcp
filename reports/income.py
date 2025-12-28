"""
Отчет по доходам
"""

from collections import defaultdict
from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions

from .base import BaseReport


class IncomeAnalysisReport(BaseReport):
    """Анализ доходов за период"""

    async def generate(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Генерация отчета по доходам"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()

        filter_params = TransactionFilter(
            year=args.get("year"), month=args.get("month")
        )

        filtered = filter_transactions(transactions, filter_params)
        # Используем правильную логику для определения доходов
        incomes = [t for t in filtered if hasattr(t, "is_income") and t.is_income]

        if not incomes:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="📊 Доходы за период не найдены")
                ]
            )

        total_income = sum(t.income for t in incomes)
        by_source = defaultdict(lambda: {"count": 0, "total": 0})
        by_category = defaultdict(float)

        # Группировка по источникам (payee)
        for t in incomes:
            source = t.payee or "Неизвестный источник"
            by_source[source]["count"] += 1
            by_source[source]["total"] += t.income

            # Группировка по категориям
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title
            by_category[cat_name] += t.income

        result = f"💰 Анализ доходов за {args['year']}"
        if args.get("month"):
            result += f"-{args['month']:02d}"
        result += f"\n\n"

        result += f"Общие доходы: +{total_income:,.2f} ₽\n"
        result += f"Количество операций: {len(incomes)}\n"
        result += f"Средний доход: {total_income / len(incomes):,.2f} ₽\n\n"

        # Топ источников доходов
        sorted_sources = sorted(
            by_source.items(), key=lambda x: x[1]["total"], reverse=True
        )
        result += "📈 Источники доходов:\n"
        for i, (source, data) in enumerate(sorted_sources[:10], 1):
            avg = data["total"] / data["count"]
            result += f"{i:2d}. {source}\n"
            result += f"    Сумма: +{data['total']:,.2f} ₽\n"
            result += f"    Операций: {data['count']}\n"
            result += f"    Средняя сумма: {avg:,.2f} ₽\n\n"

        # По категориям
        if any(by_category.values()):
            result += "📊 По категориям:\n"
            sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
            for cat_name, amount in sorted_cats:
                if amount > 0:
                    result += f"  {cat_name}: +{amount:,.2f} ₽\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
