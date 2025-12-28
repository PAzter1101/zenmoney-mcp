"""
Роутер для инструментов данных
"""

from typing import Any, Dict, Protocol

from mcp.types import CallToolResult

from src.client import ZenMoneyClient


class DataTool(Protocol):
    """Протокол для инструментов данных"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult: ...


class DataToolsRouter:
    """Роутер для маршрутизации вызовов инструментов данных"""

    def __init__(self, tools_dict: Dict[str, DataTool]):
        self.tools = tools_dict

    async def route_call(
        self, name: str, arguments: Dict[str, Any], client: ZenMoneyClient
    ) -> CallToolResult:
        """Маршрутизация вызова к соответствующему инструменту"""
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Неизвестный инструмент данных: {name}")

        return await tool.execute(client, arguments)
