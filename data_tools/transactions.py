"""
Получение транзакций
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from utils.formatters import format_transactions

from .base import BaseDataTool


class TransactionsTool(BaseDataTool):
    """Получение транзакций с фильтрацией"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение транзакций"""
        transactions = await client.get_transactions()

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

        limit = args.get("limit", 50)
        filtered = filtered[:limit]

        show_ids = args.get("show_ids", False)
        result = format_transactions(filtered, show_ids=show_ids)
        return CallToolResult(content=[TextContent(type="text", text=result)])
