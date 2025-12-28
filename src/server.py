"""
Основной MCP сервер для ДзенМани
"""

import asyncio
import os
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, Tool

from tools.data import DataTools
from tools.reports import ReportsTools


class ZenMoneyMCPServer:
    """MCP сервер для работы с ДзенМани API"""

    def __init__(self) -> None:
        self.server = Server("zenmoney-mcp")
        self.data_tools = DataTools()
        self.reports_tools = ReportsTools()
        self.token: Optional[str] = None

    def register_tools(self) -> None:
        """Регистрация всех инструментов"""

        @self.server.list_tools()
        async def list_tools() -> list:
            """Список всех доступных инструментов"""
            tools = []
            data_tools = self.data_tools.list_tools()
            reports_tools = self.reports_tools.list_tools()
            tools.extend(data_tools)
            tools.extend(reports_tools)
            return tools

        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict) -> CallToolResult:
            """Обработка вызовов инструментов"""
            if name.startswith("data_"):
                return await self.data_tools.handle_call(
                    name, arguments, self.token or ""
                )
            elif name.startswith("reports_"):
                return await self.reports_tools.handle_call(
                    name, arguments, self.token or ""
                )
            else:
                raise ValueError(f"Неизвестный инструмент: {name}")

    async def run(self) -> None:
        """Запуск сервера"""
        self.register_tools()

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def main() -> None:
    """Точка входа"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="ZenMoney MCP Server")
    parser.add_argument("--token", help="ZenMoney Bearer token")
    args = parser.parse_args()

    # Получаем токен из аргументов или переменной окружения
    token: str = args.token or os.getenv("ZENMONEY_TOKEN") or ""

    server = ZenMoneyMCPServer()

    # Если токен передан, устанавливаем его сразу
    server.token = token

    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
