"""
Получение категорий
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient
from utils.formatting import format_categories

from .base import BaseDataTool


class CategoresTool(BaseDataTool):
    """Получение категорий пользователя"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение категорий"""
        categories = await client.get_categories()
        result = format_categories(categories)
        return CallToolResult(content=[TextContent(type="text", text=result)])
