"""
Получение счетов
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient

from .base import BaseDataTool


class AccountsTool(BaseDataTool):
    """Получение информации о счетах"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение счетов"""
        accounts = await client.get_accounts()

        result = f"Всего счетов: {len(accounts)}\n\n"

        for i, (acc_id, acc) in enumerate(accounts.items(), 1):
            result += f"{i:2d}. {acc.title} ({acc.type}): {acc.balance:,.2f} ₽\n"

        return CallToolResult(content=[TextContent(type="text", text=result)])
