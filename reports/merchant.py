"""
Отчет по торговцам
"""

from typing import Dict, Any
from collections import defaultdict
from mcp.types import TextContent, CallToolResult
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from models.transaction import TransactionFilter
from .base import BaseReport

class MerchantAnalysisReport(BaseReport):
    """Анализ трат по торговцам"""
    
    async def generate(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Генерация отчета по торговцам"""
        transactions = await client.get_transactions()
        
        filter_params = TransactionFilter(
            year=args.get('year'),
            month=args.get('month')
        )
        
        filtered = filter_transactions(transactions, filter_params)
        # Используем правильную логику для определения расходов
        expenses = [t for t in filtered if hasattr(t, 'is_expense') and t.is_expense and t.payee]
        
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
