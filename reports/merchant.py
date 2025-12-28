"""
Отчет по торговцам
"""

from collections import defaultdict
from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions

from .base import BaseReport


class MerchantAnalysisReport(BaseReport):
    """Анализ трат по торговцам"""

    async def generate(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Генерация отчета по торговцам"""
        transactions = await client.get_transactions()

        filter_params = self._create_filter_params(args)

        filtered = filter_transactions(transactions, filter_params)
        # Используем правильную логику для определения расходов
        expenses = [
            t for t in filtered if hasattr(t, "is_expense") and t.is_expense and t.payee
        ]

        by_merchant: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"count": 0, "total": 0}
        )

        for t in expenses:
            payee = t.payee or "Неизвестный получатель"
            by_merchant[payee]["count"] += 1
            by_merchant[payee]["total"] += t.outcome or 0.0

        top_count = args.get("top", 10)
        sorted_merchants = sorted(
            by_merchant.items(), key=lambda x: x[1]["total"], reverse=True
        )[:top_count]

        period_desc = self._get_period_description(args)
        result = f"🏪 Топ-{top_count} торговцев за {period_desc}\n\n"

        for i, (merchant, data) in enumerate(sorted_merchants, 1):
            avg = data["total"] / data["count"]
            result += f"{i:2d}. {merchant}\n"
            result += f"    Сумма: {data['total']:,.2f} ₽\n"
            result += f"    Транзакций: {data['count']}\n"
            result += f"    Средний чек: {avg:,.2f} ₽\n\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
