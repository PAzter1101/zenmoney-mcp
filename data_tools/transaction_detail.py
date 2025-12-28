"""
Получение детальной информации о транзакции
"""

from typing import Dict, Any
from mcp.types import TextContent, CallToolResult
from src.client import ZenMoneyClient
from .base import BaseDataTool

class TransactionDetailTool(BaseDataTool):
    """Получение детальной информации о транзакции по ID"""
    
    async def execute(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Получение детальной информации о транзакции"""
        transaction_id = args.get('transaction_id')
        if not transaction_id:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Требуется ID транзакции")]
            )
        
        transactions = await client.get_transactions()
        categories = await client.get_categories()
        accounts = await client.get_accounts()
        
        # Поиск транзакции по ID
        transaction = None
        for t in transactions:
            if t.id == transaction_id:
                transaction = t
                break
        
        if not transaction:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Транзакция с ID {transaction_id} не найдена")]
            )
        
        # Формирование детального отчета
        result = f"📋 Детали транзакции\n\n"
        result += f"ID: {transaction.id}\n"
        result += f"Дата: {transaction.date}\n"
        result += f"Сумма: {transaction.amount:+.2f} ₽\n"
        
        if transaction.income:
            result += f"Доход: +{transaction.income:.2f} ₽\n"
        if transaction.outcome:
            result += f"Расход: -{transaction.outcome:.2f} ₽\n"
        
        result += f"Получатель: {transaction.payee or 'Не указан'}\n"
        
        # Категория
        if transaction.category and transaction.category in categories:
            result += f"Категория: {categories[transaction.category].title}\n"
        else:
            result += f"Категория: Без категории\n"
        
        # Счета
        if transaction.account and transaction.account in accounts:
            result += f"Счет: {accounts[transaction.account].title}\n"
        if transaction.incomeAccount and transaction.incomeAccount in accounts:
            result += f"Счет зачисления: {accounts[transaction.incomeAccount].title}\n"
        if transaction.outcomeAccount and transaction.outcomeAccount in accounts:
            result += f"Счет списания: {accounts[transaction.outcomeAccount].title}\n"
        
        # Комментарий
        if transaction.comment:
            result += f"Комментарий: {transaction.comment}\n"
        
        # Тип операции
        result += f"\nТип операции: "
        if transaction.is_transfer:
            result += "Перевод между счетами"
        elif transaction.is_income:
            result += "Доход"
        elif transaction.is_expense:
            result += "Расход"
        else:
            result += "Неопределенный"
        
        return CallToolResult(content=[TextContent(type="text", text=result)])
