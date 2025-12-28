"""
Основной MCP сервер для ДзенМани
"""

import sys
import os
import asyncio

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from tools.auth import AuthTools
from tools.data import DataTools
from tools.analysis import AnalysisTools
from tools.reports import ReportsTools

class ZenMoneyMCPServer:
    """MCP сервер для работы с ДзенМани API"""
    
    def __init__(self):
        self.server = Server("zenmoney-mcp")
        self.auth_tools = AuthTools()
        self.data_tools = DataTools()
        self.analysis_tools = AnalysisTools()
        self.reports_tools = ReportsTools()
        
    def register_tools(self):
        """Регистрация всех инструментов"""
        
        @self.server.list_tools()
        async def list_tools():
            """Список всех доступных инструментов"""
            tools = []
            tools.extend(self.auth_tools.list_tools())
            tools.extend(self.data_tools.list_tools())
            tools.extend(self.analysis_tools.list_tools())
            tools.extend(self.reports_tools.list_tools())
            return tools
        
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict):
            """Обработка вызовов инструментов"""
            token = self.auth_tools.get_token()
            
            if name.startswith("auth_"):
                return await self.auth_tools.handle_call(name, arguments)
            elif name.startswith("data_"):
                return await self.data_tools.handle_call(name, arguments, token)
            elif name.startswith("analysis_"):
                return await self.analysis_tools.handle_call(name, arguments, token)
            elif name.startswith("reports_"):
                return await self.reports_tools.handle_call(name, arguments, token)
            else:
                raise ValueError(f"Неизвестный инструмент: {name}")
    
    async def run(self):
        """Запуск сервера"""
        self.register_tools()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Точка входа"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="ZenMoney MCP Server")
    parser.add_argument("--token", help="ZenMoney Bearer token")
    args = parser.parse_args()
    
    # Получаем токен из аргументов или переменной окружения
    token = args.token or os.getenv("ZENMONEY_TOKEN")
    
    server = ZenMoneyMCPServer()
    
    # Если токен передан, устанавливаем его сразу
    if token:
        server.auth_tools.access_token = token
    
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
