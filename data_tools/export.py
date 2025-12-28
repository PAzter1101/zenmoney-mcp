"""
Экспорт данных
"""

import csv
import io
import json
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from models.transaction import Transaction

from mcp.types import CallToolResult, TextContent

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions

from .base import BaseDataTool


class DataExportTool(BaseDataTool):
    """Экспорт транзакций в различных форматах"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Экспорт транзакций"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()

        # Фильтрация
        filter_params = TransactionFilter(
            year=args.get("year"),
            month=args.get("month"),
            day=args.get("day"),
            date_from=args.get("date_from"),
            date_to=args.get("date_to"),
        )

        filtered = filter_transactions(transactions, filter_params)

        # Фильтрация по типу транзакций
        transaction_type = args.get("transaction_type", "all")
        if transaction_type == "income":
            filtered = [t for t in filtered if hasattr(t, "is_income") and t.is_income]
        elif transaction_type == "expense":
            filtered = [
                t for t in filtered if hasattr(t, "is_expense") and t.is_expense
            ]
        elif transaction_type == "transfer":
            filtered = [
                t for t in filtered if hasattr(t, "is_transfer") and t.is_transfer
            ]

        # Лимит
        limit = args.get("limit", 1000)
        filtered = filtered[:limit]

        if not filtered:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="❌ Нет транзакций для экспорта")
                ]
            )

        # Подготовка данных
        export_data = []
        for t in filtered:
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title

            export_data.append(
                {
                    "id": t.id,
                    "date": t.date,
                    "income": t.income or 0,
                    "outcome": t.outcome or 0,
                    "amount": t.amount,
                    "payee": t.payee or "",
                    "category": cat_name,
                    "comment": t.comment or "",
                    "type": self._get_transaction_type(t),
                }
            )

        # Экспорт в выбранном формате
        export_format = args.get("format", "csv")

        if export_format == "json":
            result = json.dumps(export_data, ensure_ascii=False, indent=2)
            result_text = f"📄 Экспорт {len(export_data)} транзакций в JSON:\n\n```json\n{result}\n```"
        else:  # CSV
            output = io.StringIO()
            if export_data:
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            result = output.getvalue()
            result_text = f"📄 Экспорт {len(export_data)} транзакций в CSV:\n\n```csv\n{result}\n```"

        return CallToolResult(content=[TextContent(type="text", text=result_text)])

    def _get_transaction_type(self, transaction: "Transaction") -> str:
        """Определение типа транзакции"""
        if hasattr(transaction, "is_income") and transaction.is_income:
            return "income"
        elif hasattr(transaction, "is_expense") and transaction.is_expense:
            return "expense"
        elif hasattr(transaction, "is_transfer") and transaction.is_transfer:
            return "transfer"
        else:
            return "other"
