"""
Инструменты отчетов для MCP сервера
"""

from mcp.types import Tool, TextContent, CallToolResult
from typing import Dict, Any, List
from collections import defaultdict
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from utils.formatters import format_spending_report
from models.transaction import TransactionFilter

class ReportsTools:
    """Класс инструментов отчетов"""
    
    def list_tools(self) -> List[Tool]:
        """Список инструментов отчетов"""
        return [
            Tool(
                name="reports_spending",
                description="Отчет по тратам за период",
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
                name="reports_category_breakdown",
                description="Разбивка трат по категориям",
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
                name="reports_merchant_analysis",
                description="Анализ трат по торговцам",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Год"},
                        "month": {"type": "integer", "description": "Месяц (опционально)"},
                        "top": {"type": "integer", "description": "Количество топ торговцев", "default": 10}
                    },
                    "required": ["year"]
                }
            )
        ]
    
    async def handle_call(self, name: str, arguments: Dict[str, Any], token: str) -> CallToolResult:
        """Обработка вызовов инструментов отчетов"""
        
        if not token:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется аутентификация")]
            )
        
        try:
            client = ZenMoneyClient(token)
            
            if name == "reports_spending":
                return await self._spending_report(client, arguments)
            elif name == "reports_category_breakdown":
                return await self._category_breakdown(client, arguments)
            elif name == "reports_merchant_analysis":
                return await self._merchant_analysis(client, arguments)
            else:
                raise ValueError(f"Неизвестный инструмент отчетов: {name}")
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Ошибка создания отчета: {e}")]
            )
    
    async def _spending_report(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Отчет по тратам"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        expenses = [t for t in filtered if t.is_expense]
        
        if not expenses:
            return CallToolResult(
                content=[TextContent(type="text", text="📊 Расходы за период не найдены")]
            )
        
        total_expenses = sum(t.outcome for t in expenses)
        by_category = defaultdict(float)
        
        for t in expenses:
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title
            by_category[cat_name] += t.outcome
        
        report_data = {
            'total_expenses': total_expenses,
            'transaction_count': len(expenses),
            'average_expense': total_expenses / len(expenses) if expenses else 0,
            'by_category': dict(by_category)
        }
        
        result = format_spending_report(report_data)
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _category_breakdown(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Разбивка по категориям"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        
        by_category = defaultdict(lambda: {'count': 0, 'income': 0, 'outcome': 0})
        
        for t in filtered:
            cat_name = "Без категории"
            if t.category and t.category in categories:
                cat_name = categories[t.category].title
            
            by_category[cat_name]['count'] += 1
            by_category[cat_name]['income'] += t.income
            by_category[cat_name]['outcome'] += t.outcome
        
        result = f"📊 Разбивка по категориям за {args['year']}"
        if args.get('month'):
            result += f"-{args['month']:02d}"
        result += f"\n\n"
        
        sorted_cats = sorted(by_category.items(), key=lambda x: x[1]['outcome'], reverse=True)
        
        for cat_name, data in sorted_cats:
            result += f"{cat_name}:\n"
            result += f"  Транзакций: {data['count']}\n"
            result += f"  Доходы: +{data['income']:,.2f} ₽\n"
            result += f"  Расходы: -{data['outcome']:,.2f} ₽\n"
            result += f"  Баланс: {data['income'] - data['outcome']:+,.2f} ₽\n\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
    
    async def _merchant_analysis(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Анализ по торговцам"""
        transactions = await client.get_transactions()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        expenses = [t for t in filtered if t.is_expense and t.payee]
        
        by_merchant = defaultdict(lambda: {'count': 0, 'total': 0})
        
        for t in expenses:
            by_merchant[t.payee]['count'] += 1
            by_merchant[t.payee]['total'] += t.outcome
        
        top_count = args.get('top', 10)
        sorted_merchants = sorted(by_merchant.items(), key=lambda x: x[1]['total'], reverse=True)[:top_count]
        
        result = f"🏪 Топ-{top_count} торговцев за {args['year']}"
        if args.get('month'):
            result += f"-{args['month']:02d}"
        result += f"\n\n"
        
        for i, (merchant, data) in enumerate(sorted_merchants, 1):
            avg = data['total'] / data['count']
            result += f"{i:2d}. {merchant}\n"
            result += f"    Сумма: {data['total']:,.2f} ₽\n"
            result += f"    Транзакций: {data['count']}\n"
            result += f"    Средний чек: {avg:,.2f} ₽\n\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
