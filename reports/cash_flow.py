"""
Отчет по денежному потоку
"""

from typing import Dict, Any
from mcp.types import TextContent, CallToolResult
from src.client import ZenMoneyClient
from utils.filters import filter_transactions
from .base import BaseReport

class CashFlowReport(BaseReport):
    """Отчет по денежному потоку (доходы vs расходы)"""
    
    async def generate(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Генерация отчета по денежному потоку"""
        transactions = await client.get_transactions()
        
        filter_params = self._create_filter_params(args)
        filtered = filter_transactions(transactions, filter_params)
        
        # Используем правильную логику для определения доходов и расходов
        incomes = [t for t in filtered if hasattr(t, 'is_income') and t.is_income]
        expenses = [t for t in filtered if hasattr(t, 'is_expense') and t.is_expense]
        transfers = [t for t in filtered if hasattr(t, 'is_transfer') and t.is_transfer]
        
        total_income = sum(t.income for t in incomes)
        total_expenses = sum(t.outcome for t in expenses)
        net_flow = total_income - total_expenses
        
        period_desc = self._get_period_description(args)
        result = f"💰 Денежный поток за {period_desc}\n\n"
        
        result += f"📈 Доходы: +{total_income:,.2f} ₽ ({len(incomes)} операций)\n"
        result += f"📉 Расходы: -{total_expenses:,.2f} ₽ ({len(expenses)} операций)\n"
        result += f"🔄 Переводы: {len(transfers)} операций (исключены из расчета)\n\n"
        
        result += f"💵 Чистый поток: {net_flow:+,.2f} ₽\n"
        
        if net_flow > 0:
            result += "✅ Положительный денежный поток (доходы превышают расходы)\n"
        elif net_flow < 0:
            result += "⚠️ Отрицательный денежный поток (расходы превышают доходы)\n"
        else:
            result += "⚖️ Нулевой денежный поток (доходы равны расходам)\n"
        
        # Дополнительная статистика
        if incomes and expenses:
            result += f"\n📊 Статистика:\n"
            result += f"  Средний доход: {total_income / len(incomes):,.2f} ₽\n"
            result += f"  Средний расход: {total_expenses / len(expenses):,.2f} ₽\n"
            result += f"  Соотношение доходы/расходы: {total_income / total_expenses:.2f}\n"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
