"""
Инструменты отчетов для MCP сервера
"""

from typing import Any, Dict, List

from mcp.types import CallToolResult, TextContent, Tool

from reports.cash_flow import CashFlowReport
from reports.category import CategoryBreakdownReport
from reports.income import IncomeAnalysisReport
from reports.merchant import MerchantAnalysisReport
from reports.spending import SpendingReport
from src.client import ZenMoneyClient


class ReportsTools:
    """Класс инструментов отчетов"""

    def __init__(self) -> None:
        self.spending_report = SpendingReport()
        self.category_report = CategoryBreakdownReport()
        self.merchant_report = MerchantAnalysisReport()
        self.income_report = IncomeAnalysisReport()
        self.cash_flow_report = CashFlowReport()

    def _get_date_input_schema(self) -> Dict[str, Any]:
        """Универсальная схема параметров даты для отчетов"""
        return {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Год (например, 2025)"},
                "month": {"type": "integer", "description": "Месяц (например, 12)"},
                "day": {"type": "integer", "description": "День (например, 15)"},
                "date_from": {
                    "type": "string",
                    "description": "Дата начала в формате YYYY-MM-DD",
                },
                "date_to": {
                    "type": "string",
                    "description": "Дата окончания в формате YYYY-MM-DD",
                },
            },
        }

    def list_tools(self) -> List[Tool]:
        """Список инструментов отчетов"""
        base_schema = self._get_date_input_schema()

        return [
            Tool(
                name="reports_spending",
                description="Отчет по тратам за период",
                inputSchema=base_schema,
            ),
            Tool(
                name="reports_category_breakdown",
                description="Разбивка трат по категориям",
                inputSchema=base_schema,
            ),
            Tool(
                name="reports_merchant_analysis",
                description="Анализ трат по торговцам",
                inputSchema={
                    **base_schema,
                    "properties": {
                        **base_schema["properties"],
                        "top": {
                            "type": "integer",
                            "description": "Количество топ торговцев",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="reports_income_analysis",
                description="Анализ доходов за период",
                inputSchema=base_schema,
            ),
            Tool(
                name="reports_cash_flow",
                description="Денежный поток: доходы vs расходы за период",
                inputSchema=base_schema,
            ),
        ]

    async def handle_call(
        self, name: str, arguments: Dict[str, Any], token: str
    ) -> CallToolResult:
        """Обработка вызовов инструментов отчетов"""

        if not token:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется аутентификация")]
            )

        try:
            client = ZenMoneyClient(token)

            if name == "reports_spending":
                return await self.spending_report.generate(client, arguments)
            elif name == "reports_category_breakdown":
                return await self.category_report.generate(client, arguments)
            elif name == "reports_merchant_analysis":
                return await self.merchant_report.generate(client, arguments)
            elif name == "reports_income_analysis":
                return await self.income_report.generate(client, arguments)
            elif name == "reports_cash_flow":
                return await self.cash_flow_report.generate(client, arguments)
            else:
                raise ValueError(f"Неизвестный инструмент отчетов: {name}")

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"❌ Ошибка создания отчета: {e}")
                ]
            )
