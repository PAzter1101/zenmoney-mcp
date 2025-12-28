"""
Детальное форматирование транзакций
"""

from typing import Dict, List

from models.account import Account
from models.category import Category
from models.transaction import Transaction


class TransactionDetailFormatter:
    """Форматтер для детальной информации о транзакции"""

    def format_transaction_details(
        self,
        transaction: Transaction,
        transactions: List[Transaction],
        categories: Dict[str, Category],
        accounts: Dict[str, Account],
    ) -> str:
        """Форматирование полной информации о транзакции"""
        parts = [
            "📋 Детали транзакции\n",
            f"ID: {transaction.id}",
            f"Дата: {transaction.date}",
            f"Сумма: {transaction.amount:+.2f} ₽",
            self._format_amounts(transaction),
            f"Получатель: {transaction.payee or 'Не указан'}",
            self._format_category(transaction, categories),
            self._format_accounts(transaction, accounts),
            self._format_optional_fields(transaction),
            self._format_receipt_info(transaction),
            self._format_geolocation(transaction),
            self._format_transaction_type(transaction, transactions),
        ]
        return "\n".join(filter(None, parts))

    def _format_amounts(self, transaction: Transaction) -> str:
        parts = []
        if transaction.income:
            parts.append(f"Доход: +{transaction.income:.2f} ₽")
        if transaction.outcome:
            parts.append(f"Расход: -{transaction.outcome:.2f} ₽")
        return "\n".join(parts)

    def _format_category(
        self, transaction: Transaction, categories: Dict[str, Category]
    ) -> str:
        category_name = "Без категории"
        if transaction.category and transaction.category in categories:
            category_name = categories[transaction.category].title
        elif transaction.tag and transaction.tag[0] in categories:
            category_name = categories[transaction.tag[0]].title
        return f"Категория: {category_name}"

    def _format_accounts(
        self, transaction: Transaction, accounts: Dict[str, Account]
    ) -> str:
        parts = []
        if transaction.account and transaction.account in accounts:
            parts.append(f"Счет: {accounts[transaction.account].title}")
        if transaction.incomeAccount and transaction.incomeAccount in accounts:
            parts.append(
                f"Счет зачисления: {accounts[transaction.incomeAccount].title}"
            )
        if transaction.outcomeAccount and transaction.outcomeAccount in accounts:
            parts.append(f"Счет списания: {accounts[transaction.outcomeAccount].title}")
        return "\n".join(parts)

    def _format_optional_fields(self, transaction: Transaction) -> str:
        parts = []
        if transaction.comment:
            parts.append(f"Комментарий: {transaction.comment}")
        if transaction.originalPayee and transaction.originalPayee != transaction.payee:
            parts.append(f"Исходный получатель: {transaction.originalPayee}")
        if transaction.source:
            parts.append(f"Источник: {transaction.source}")
        return "\n".join(parts)

    def _format_transaction_type(
        self, transaction: Transaction, transactions: List[Transaction]
    ) -> str:
        if transaction.is_transfer(transactions) is True:
            type_name = "Перевод между счетами"
        elif transaction.is_income:
            type_name = "Доход"
        elif transaction.is_expense(transactions) is True:
            type_name = "Расход"
        else:
            type_name = "Неопределенный"
        return f"\nТип операции: {type_name}"

    def _format_receipt_info(self, transaction: Transaction) -> str:
        """Форматирование информации о чеке"""
        if not transaction.qrCode:
            return ""

        result = "\n📄 Данные чека:\n"
        result += f"QR-код: {transaction.qrCode}\n"

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

        return result

    def _format_geolocation(self, transaction: Transaction) -> str:
        """Форматирование геолокации"""
        if transaction.latitude and transaction.longitude:
            result = "\n📍 Местоположение:\n"
            result += f"Координаты: {transaction.latitude}, {transaction.longitude}\n"
            return result
        return ""
