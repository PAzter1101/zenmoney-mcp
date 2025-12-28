"""
Инструменты получения данных для MCP сервера
"""

from mcp.types import Tool, TextContent, CallToolResult
from typing import Dict, Any, List
from src.client import ZenMoneyClient
from utils.formatters import format_transactions, format_categories

class DataTools:
    """Класс инструментов получения данных"""
    
    def list_tools(self) -> List[Tool]:
        """Список инструментов получения данных"""
        return [
            Tool(
                name="data_get_transactions",
                description="Получить транзакции с фильтрацией по периоду",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Год (например, 2025)"},
                        "month": {"type": "integer", "description": "Месяц (например, 1)"},
                        "limit": {"type": "integer", "description": "Лимит транзакций (по умолчанию 50)"}
                    }
                }
            ),
            Tool(
                name="data_get_categories",
                description="Получить все категории пользователя",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="data_get_accounts",
                description="Получить информацию о счетах пользователя",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="data_get_merchants",
                description="Получить список торговцев/получателей",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Лимит результатов (по умолчанию 50)"}
                    }
                }
            )
        ]
    
    async def handle_call(self, name: str, arguments: Dict[str, Any], auth_token: str) -> CallToolResult:
        """Обработка вызовов инструментов данных"""
        
        if not auth_token:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется аутентификация")]
            )
        
        try:
            client = ZenMoneyClient(auth_token)
            
            if name == "data_get_transactions":
                return await self._get_transactions(client, arguments)
            elif name == "data_get_categories":
                return await self._get_categories(client)
            elif name == "data_get_accounts":
                return await self._get_accounts(client)
            elif name == "data_get_merchants":
                return await self._get_merchants(client, arguments)
            else:
                raise ValueError(f"Неизвестный инструмент данных: {name}")
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Ошибка получения данных: {e}")]
            )
    
    async def _get_transactions(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Получение транзакций"""
        transactions = await client.get_transactions()
        
        # Фильтрация
        year = args.get('year')
        month = args.get('month')
        limit = args.get('limit', 50)
        
        if year:
            year_str = str(year)
            if month:
                prefix = f"{year_str}-{month:02d}"
            else:
                prefix = year_str
            transactions = [t for t in transactions if t.date.startswith(prefix)]
        
        transactions = transactions[:limit]
        result = format_transactions(transactions)
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _get_categories(self, client: ZenMoneyClient) -> CallToolResult:
        """Получение категорий"""
        categories = await client.get_categories()
        result = format_categories(categories)
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _get_accounts(self, client: ZenMoneyClient) -> CallToolResult:
        """Получение счетов"""
        accounts = await client.get_accounts()
        
        result = f"Всего счетов: {len(accounts)}\n\n"
        
        for i, (acc_id, acc) in enumerate(accounts.items(), 1):
            result += f"{i:2d}. {acc.title} ({acc.type}): {acc.balance:,.2f} ₽\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _get_merchants(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Получение торговцев"""
        transactions = await client.get_transactions()
        
        # Собираем статистику по торговцам
        merchants = {}
        for t in transactions:
            if t.payee and t.is_expense:
                if t.payee not in merchants:
                    merchants[t.payee] = {'count': 0, 'total': 0}
                merchants[t.payee]['count'] += 1
                merchants[t.payee]['total'] += t.outcome
        
        limit = args.get('limit', 50)
        sorted_merchants = sorted(merchants.items(), key=lambda x: x[1]['total'], reverse=True)[:limit]
        
        result = f"Найдено торговцев: {len(sorted_merchants)}\n\n"
        
        for i, (merchant, data) in enumerate(sorted_merchants, 1):
            result += f"{i:2d}. {merchant}\n"
            result += f"    Транзакций: {data['count']}\n"
            result += f"    Общая сумма: {data['total']:,.2f} ₽\n\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
