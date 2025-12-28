"""
Получение торговцев
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient

from .base import BaseDataTool


class MerchantsTool(BaseDataTool):
    """Получение списка торговцев/получателей"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение торговцев"""
        transactions = await client.get_transactions()

        # Собираем статистику по торговцам
        merchants = {}
        for t in transactions:
            if t.payee and t.is_expense(transactions) is True:
                if t.payee not in merchants:
                    merchants[t.payee] = {"count": 0, "total": 0.0}
                merchants[t.payee]["count"] += 1
                merchants[t.payee]["total"] += t.outcome or 0.0

        limit = args.get("limit", 50)
        sorted_merchants = sorted(
            merchants.items(), key=lambda x: x[1]["total"], reverse=True
        )[:limit]

        result = f"Найдено торговцев: {len(sorted_merchants)}\n\n"

        for i, (merchant, data) in enumerate(sorted_merchants, 1):
            result += f"{i:2d}. {merchant}\n"
            result += f"    Транзакций: {data['count']}\n"
            result += f"    Общая сумма: {data['total']:,.2f} ₽\n\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
