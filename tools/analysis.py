"""
Инструменты анализа данных для MCP сервера
"""

from mcp.types import Tool, TextContent, CallToolResult
from typing import Dict, Any, List
from src.client import ZenMoneyClient
from utils.filters import filter_transactions, find_duplicates
from utils.formatters import format_transactions
from models.transaction import TransactionFilter

class AnalysisTools:
    """Класс инструментов анализа"""
    
    def list_tools(self) -> List[Tool]:
        """Список инструментов анализа"""
        return [
            Tool(
                name="analysis_period",
                description="Анализ транзакций за период",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Год"},
                        "month": {"type": "integer", "description": "Месяц (опционально)"}
                    },
                    "required": ["year"]
                }
            ),
            Tool(
                name="analysis_find_uncategorized",
                description="Поиск некатегоризированных транзакций",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Год"},
                        "month": {"type": "integer", "description": "Месяц (опционально)"}
                    },
                    "required": ["year"]
                }
            ),
            Tool(
                name="analysis_detect_duplicates",
                description="Поиск возможных дублей транзакций",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Год"},
                        "month": {"type": "integer", "description": "Месяц (опционально)"}
                    },
                    "required": ["year"]
                }
            )
        ]
    
    async def handle_call(self, name: str, arguments: Dict[str, Any], token: str) -> CallToolResult:
        """Обработка вызовов инструментов анализа"""
        
        if not token:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется аутентификация")]
            )
        
        try:
            client = ZenMoneyClient(token)
            
            if name == "analysis_period":
                return await self._analyze_period(client, arguments)
            elif name == "analysis_find_uncategorized":
                return await self._find_uncategorized(client, arguments)
            elif name == "analysis_detect_duplicates":
                return await self._detect_duplicates(client, arguments)
            else:
                raise ValueError(f"Неизвестный инструмент анализа: {name}")
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Ошибка анализа: {e}")]
            )
    
    async def _analyze_period(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Анализ транзакций за период"""
        transactions = await client.get_transactions()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        
        total_income = sum(t.income for t in filtered)
        total_outcome = sum(t.outcome for t in filtered)
        uncategorized = len([t for t in filtered if not t.category])
        
        result = f"📊 Анализ за {args['year']}"
        if args.get('month'):
            result += f"-{args['month']:02d}"
        result += f"\n\n"
        result += f"Всего транзакций: {len(filtered)}\n"
        result += f"Доходы: +{total_income:,.2f} ₽\n"
        result += f"Расходы: -{total_outcome:,.2f} ₽\n"
        result += f"Баланс: {total_income - total_outcome:+,.2f} ₽\n"
        result += f"Без категории: {uncategorized} транзакций\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _find_uncategorized(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Поиск некатегоризированных транзакций"""
        transactions = await client.get_transactions()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month'),
            uncategorized_only=True
        )
        
        uncategorized = filter_transactions(transactions, filter_params)
        
        if not uncategorized:
            return CallToolResult(
                content=[TextContent(type="text", text="✅ Все транзакции категоризированы")]
            )
        
        result = format_transactions(uncategorized)
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _detect_duplicates(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Поиск дублей транзакций"""
        transactions = await client.get_transactions()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        duplicates = find_duplicates(filtered)
        
        if not duplicates:
            return CallToolResult(
                content=[TextContent(type="text", text="✅ Дубли не найдены")]
            )
        
        result = f"🔍 Найдено групп дублей: {len(duplicates)}\n\n"
        
        for i, group in enumerate(duplicates, 1):
            result += f"Группа {i}:\n"
            for t in group:
                result += f"  {t.date} | {t.amount:+.2f} | {t.payee or 'Без получателя'}\n"
            result += "\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
