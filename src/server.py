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

from tools.data import DataTools
from tools.reports import ReportsTools

class ZenMoneyMCPServer:
    """MCP сервер для работы с ДзенМани API"""
    
    def __init__(self):
        self.server = Server("zenmoney-mcp")
        self.data_tools = DataTools()
        self.reports_tools = ReportsTools()
        self.token = None
        
    def register_tools(self):
        """Регистрация всех инструментов"""
        
        @self.server.list_tools()
        async def list_tools():
            """Список всех доступных инструментов"""
            import sys
            print("DEBUG: Запрос списка инструментов", file=sys.stderr)
            
            tools = []
            try:
                data_tools = self.data_tools.list_tools()
                reports_tools = self.reports_tools.list_tools()
                tools.extend(data_tools)
                tools.extend(reports_tools)
                
                print(f"DEBUG: Загружено {len(tools)} инструментов:", file=sys.stderr)
                for tool in tools:
                    print(f"  - {tool.name}", file=sys.stderr)
                    
                return tools
            except Exception as e:
                print(f"DEBUG: Ошибка при загрузке инструментов: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                raise
        
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict):
            """Обработка вызовов инструментов"""
            
            # Логирование для отладки
            import sys
            print(f"DEBUG: Вызов инструмента '{name}' с аргументами: {arguments}", file=sys.stderr)
            
            try:
                if name.startswith("data_"):
                    result = await self.data_tools.handle_call(name, arguments, self.token)
                    print(f"DEBUG: Инструмент '{name}' выполнен успешно", file=sys.stderr)
                    return result
                elif name.startswith("reports_"):
                    result = await self.reports_tools.handle_call(name, arguments, self.token)
                    print(f"DEBUG: Инструмент '{name}' выполнен успешно", file=sys.stderr)
                    return result
                else:
                    error_msg = f"Неизвестный инструмент: {name}"
                    print(f"DEBUG: {error_msg}", file=sys.stderr)
                    raise ValueError(error_msg)
            except Exception as e:
                print(f"DEBUG: Ошибка при выполнении '{name}': {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                raise
    
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
        server.token = token
    
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
