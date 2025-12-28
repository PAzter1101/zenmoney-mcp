"""
Получение детальной информации о транзакции
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient

from .base import BaseDataTool


class TransactionDetailTool(BaseDataTool):
    """Получение детальной информации о транзакции по ID"""

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Получение детальной информации о транзакции"""
        transaction_id = args.get("transaction_id")
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
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Транзакция с ID {transaction_id} не найдена",
                    )
                ]
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
        category_name = "Без категории"
        if transaction.category and transaction.category in categories:
            category_name = categories[transaction.category].title
        elif transaction.tag:
            # Берем первую категорию из массива тегов
            first_tag = transaction.tag[0]
            if first_tag in categories:
                category_name = categories[first_tag].title
            
        result += f"Категория: {category_name}\n"

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

        # Информация о чеке
        if transaction.qrCode:
            result += f"\n📄 Данные чека:\n"
            result += f"QR-код: {transaction.qrCode}\n"

            # Парсим QR-код чека
            qr_params = {}
            for param in transaction.qrCode.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    qr_params[key] = value

            if "t" in qr_params:
                result += f"Время: {qr_params['t']}\n"
            if "s" in qr_params:
                result += f"Сумма чека: {qr_params['s']} ₽\n"
            if "fn" in qr_params:
                result += f"Фискальный номер: {qr_params['fn']}\n"
            if "i" in qr_params:
                result += f"Номер документа: {qr_params['i']}\n"
            if "fp" in qr_params:
                result += f"Фискальный признак: {qr_params['fp']}\n"

        # Геолокация
        if transaction.latitude and transaction.longitude:
            result += f"\n📍 Местоположение:\n"
            result += f"Координаты: {transaction.latitude}, {transaction.longitude}\n"

        # Дополнительная информация
        if transaction.originalPayee and transaction.originalPayee != transaction.payee:
            result += f"Исходный получатель: {transaction.originalPayee}\n"

        if transaction.source:
            result += f"Источник: {transaction.source}\n"

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
