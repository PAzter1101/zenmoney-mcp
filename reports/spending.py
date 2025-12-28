"""
Отчет по тратам
"""

from typing import Dict, Any
from collections import defaultdict
from mcp.types import TextContent, CallToolResult
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from utils.formatters import format_spending_report
from models.transaction import TransactionFilter
from .base import BaseReport

class SpendingReport(BaseReport):
    """Отчет по тратам за период"""
    
    async def generate(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Генерация отчета по тратам"""
        transactions = await client.get_transactions()
        categories = await client.get_categories()
        
        filter_params = self._create_filter_params(args)
        filtered = filter_transactions(transactions, filter_params)
        
        # Отладочная информация
        debug_info = f"Всего транзакций: {len(filtered)}\n"
        transfers = [t for t in filtered if hasattr(t, 'is_transfer') and t.is_transfer]
        expenses = [t for t in filtered if hasattr(t, 'is_expense') and t.is_expense]
        
        debug_info += f"Переводы между счетами: {len(transfers)}\n"
        debug_info += f"Реальные расходы: {len(expenses)}\n\n"
        
        # Показать примеры переводов
        if transfers:
            debug_info += "Примеры переводов:\n"
            for t in transfers[:3]:
                debug_info += f"  {t.date} | -{t.outcome:,.2f} | {t.payee or 'Без получателя'} | inc_acc: {bool(t.incomeAccount)} | out_acc: {bool(t.outcomeAccount)}\n"
            debug_info += "\n"
        
        # Показать примеры расходов
        if expenses:
            debug_info += "Примеры расходов:\n"
            for t in expenses[:3]:
                debug_info += f"  {t.date} | -{t.outcome:,.2f} | {t.payee or 'Без получателя'} | inc_acc: {bool(t.incomeAccount)} | out_acc: {bool(t.outcomeAccount)}\n"
            debug_info += "\n"
        
        if not expenses:
            return CallToolResult(
                content=[TextContent(type="text", text=f"{debug_info}📊 Расходы за период не найдены")]
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
        
        period_desc = self._get_period_description(args)
        result = debug_info + f"📊 Отчет по тратам за {period_desc}\n\n"
        result += f"Общие траты: {total_expenses:,.2f} ₽\n"
        result += f"Количество транзакций: {len(expenses)}\n"
        result += f"Средняя трата: {total_expenses / len(expenses):,.2f} ₽\n\n"
        
        if by_category:
            result += "По категориям:\n"
            for cat_name, amount in by_category.items():
                result += f"  {cat_name}: {amount:,.2f} ₽\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
