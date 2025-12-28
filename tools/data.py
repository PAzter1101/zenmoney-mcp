"""
Инструменты получения данных для MCP сервера
"""

from typing import Any, Dict, List

from mcp.types import CallToolResult, TextContent, Tool

from data_tools.accounts import AccountsTool
from data_tools.categories import CategoresTool
from data_tools.export import DataExportTool
from data_tools.merchants import MerchantsTool
from data_tools.transaction_detail import TransactionDetailTool
from data_tools.transactions import TransactionsTool
from data_tools.update_transaction import UpdateTransactionTool
from src.client import ZenMoneyClient
from utils.data_router import DataToolsRouter


class DataTools:
    """Класс инструментов получения данных"""

    def __init__(self) -> None:
        self.transactions_tool = TransactionsTool()
        self.transaction_detail_tool = TransactionDetailTool()
        self.categories_tool = CategoresTool()
        self.accounts_tool = AccountsTool()
        self.merchants_tool = MerchantsTool()
        self.export_tool = DataExportTool()
        self.update_transaction_tool = UpdateTransactionTool()

        self.router = DataToolsRouter(
            {
                "data_get_transactions": self.transactions_tool,
                "data_get_transaction_detail": self.transaction_detail_tool,
                "data_get_categories": self.categories_tool,
                "data_get_accounts": self.accounts_tool,
                "data_get_merchants": self.merchants_tool,
                "data_export": self.export_tool,
                "data_set_transaction": self.update_transaction_tool,
            }
        )

    def list_tools(self) -> List[Tool]:
        """Список инструментов получения данных"""
        return [
            Tool(
                name="data_get_transactions",
                description="Получить транзакции с фильтрацией по периоду",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Год (например, 2025)",
                        },
                        "month": {
                            "type": "integer",
                            "description": "Месяц (например, 1)",
                        },
                        "day": {
                            "type": "integer",
                            "description": "День (например, 15)",
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Дата начала в формате YYYY-MM-DD",
                        },
                        "date_to": {
                            "type": "string",
                            "description": "Дата окончания в формате YYYY-MM-DD",
                        },
                        "payee": {
                            "type": "string",
                            "description": "Поиск по получателю (частичное совпадение)",
                        },
                        "show_ids": {
                            "type": "boolean",
                            "description": "Показывать ID транзакций",
                            "default": False,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Лимит транзакций (по умолчанию 50)",
                        },
                    },
                },
            ),
            Tool(
                name="data_get_transaction_detail",
                description="Получить детальную информацию о транзакции по ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "ID транзакции",
                        }
                    },
                    "required": ["transaction_id"],
                },
            ),
            Tool(
                name="data_get_categories",
                description="Получить все категории пользователя",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="data_get_accounts",
                description="Получить информацию о счетах пользователя",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="data_get_merchants",
                description="Получить список торговцев/получателей",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Лимит результатов (по умолчанию 50)",
                        }
                    },
                },
            ),
            Tool(
                name="data_export",
                description="Экспорт транзакций в различных форматах",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Год (например, 2025)",
                        },
                        "month": {
                            "type": "integer",
                            "description": "Месяц (например, 12)",
                        },
                        "day": {
                            "type": "integer",
                            "description": "День (например, 15)",
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Дата начала в формате YYYY-MM-DD",
                        },
                        "date_to": {
                            "type": "string",
                            "description": "Дата окончания в формате YYYY-MM-DD",
                        },
                        "format": {
                            "type": "string",
                            "description": "Формат экспорта",
                            "enum": ["csv", "json"],
                            "default": "csv",
                        },
                        "transaction_type": {
                            "type": "string",
                            "description": "Тип транзакций для экспорта",
                            "enum": ["all", "income", "expense", "transfer"],
                            "default": "all",
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Максимальное количество транзакций "
                                "(по умолчанию 1000)"
                            ),
                        },
                    },
                },
            ),
            Tool(
                name="data_set_transaction",
                description=(
                    "Обновление данных транзакции " "(категория, комментарий и др.)"
                ),
                inputSchema=self.update_transaction_tool.input_schema,
            ),
        ]

    async def handle_call(
        self, name: str, arguments: Dict[str, Any], auth_token: str
    ) -> CallToolResult:
        """Обработка вызовов инструментов данных"""
        if not auth_token:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется аутентификация")]
            )

        try:
            client = ZenMoneyClient(auth_token)
            return await self.router.route_call(name, arguments, client)
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"❌ Ошибка получения данных: {e}")
                ]
            )
