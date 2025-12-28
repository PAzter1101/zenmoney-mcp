"""
Получение детальной информации о транзакции
"""

from typing import Any, Dict, List, Optional

from mcp.types import CallToolResult, TextContent

from models.transaction import Transaction
from src.client import ZenMoneyClient
from utils.formatting import TransactionDetailFormatter

from .base import BaseDataTool


class TransactionDetailTool(BaseDataTool):
    """Получение детальной информации о транзакции по ID"""

    def __init__(self) -> None:
        self.formatter = TransactionDetailFormatter()

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение детальной информации о транзакции"""
        transaction_id = args.get("transaction_id")
        if not transaction_id:
            return self._error_result("❌ Требуется ID транзакции")

        transactions = await client.get_transactions()
        categories = await client.get_categories()
        accounts = await client.get_accounts()

        transaction = self._find_transaction(transactions, transaction_id)
        if not transaction:
            return self._error_result(f"❌ Транзакция с ID {transaction_id} не найдена")

        result = self.formatter.format_transaction_details(
            transaction, transactions, categories, accounts
        )
        return CallToolResult(content=[TextContent(type="text", text=result)])

    def _error_result(self, message: str) -> CallToolResult:
        return CallToolResult(content=[TextContent(type="text", text=message)])

    def _find_transaction(
        self, transactions: List[Transaction], transaction_id: str
    ) -> Optional[Transaction]:
        return next((t for t in transactions if t.id == transaction_id), None)
