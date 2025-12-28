"""
Юнит-тесты для инструмента TransactionDetailTool
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock

from data_tools.transaction_detail import TransactionDetailTool
from models.transaction import Transaction
from src.client import ZenMoneyClient


class TestTransactionDetailTool(unittest.TestCase):
    """Тесты для инструмента детализации транзакций"""

    def setUp(self):
        """Настройка тестов"""
        self.tool = TransactionDetailTool()
        self.mock_client = Mock(spec=ZenMoneyClient)

    def test_tool_creation(self):
        """Тест создания инструмента"""
        self.assertIsNotNone(self.tool)
        self.assertIsInstance(self.tool, TransactionDetailTool)

    def test_missing_transaction_id(self):
        """Тест обработки отсутствующего ID транзакции"""

        async def run_test():
            result = await self.tool.execute(self.mock_client, {})
            self.assertIn("Требуется ID транзакции", result.content[0].text)

        asyncio.run(run_test())

    def test_transaction_not_found(self):
        """Тест обработки несуществующей транзакции"""
        self.mock_client.get_transactions = AsyncMock(return_value=[])
        self.mock_client.get_categories = AsyncMock(return_value={})
        self.mock_client.get_accounts = AsyncMock(return_value={})

        async def run_test():
            result = await self.tool.execute(
                self.mock_client, {"transaction_id": "non-existent"}
            )
            self.assertIn("не найдена", result.content[0].text)

        asyncio.run(run_test())

    def test_basic_transaction_details(self):
        """Тест отображения базовых деталей транзакции"""
        mock_transaction = Transaction(
            id="basic-transaction",
            date="2025-01-01",
            income=0,
            outcome=500,
            payee="Test Store",
        )

        self.mock_client.get_transactions = AsyncMock(return_value=[mock_transaction])
        self.mock_client.get_categories = AsyncMock(return_value={})
        self.mock_client.get_accounts = AsyncMock(return_value={})

        async def run_test():
            result = await self.tool.execute(
                self.mock_client, {"transaction_id": "basic-transaction"}
            )
            content = result.content[0].text

            self.assertIn("basic-transaction", content)
            self.assertIn("2025-01-01", content)
            self.assertIn("-500.00", content)
            self.assertIn("Test Store", content)
            self.assertIn("Расход", content)

        asyncio.run(run_test())

    def test_transaction_with_receipt(self):
        """Тест транзакции с чеком"""
        qr_code = "t=20250915T1918&s=470.00&fn=123456&i=789&fp=999&n=1"

        mock_transaction = Transaction(
            id="receipt-transaction",
            date="2025-09-15",
            outcome=470,
            payee="SAMOKAT",
            qrCode=qr_code,
        )

        self.mock_client.get_transactions = AsyncMock(return_value=[mock_transaction])
        self.mock_client.get_categories = AsyncMock(return_value={})
        self.mock_client.get_accounts = AsyncMock(return_value={})

        async def run_test():
            result = await self.tool.execute(
                self.mock_client, {"transaction_id": "receipt-transaction"}
            )
            content = result.content[0].text

            # Проверяем основные данные
            self.assertIn("receipt-transaction", content)
            self.assertIn("SAMOKAT", content)

            # Проверяем данные чека
            self.assertIn("Данные чека", content)
            self.assertIn("QR-код:", content)
            self.assertIn("Время: 20250915T1918", content)
            self.assertIn("Сумма чека: 470.00", content)
            self.assertIn("Фискальный номер: 123456", content)
            self.assertIn("Номер документа: 789", content)
            self.assertIn("Фискальный признак: 999", content)

        asyncio.run(run_test())

    def test_transaction_with_geolocation(self):
        """Тест транзакции с геолокацией"""
        mock_transaction = Transaction(
            id="geo-transaction",
            date="2025-01-01",
            outcome=300,
            payee="Local Store",
            latitude=55.7558,
            longitude=37.6176,
        )

        self.mock_client.get_transactions = AsyncMock(return_value=[mock_transaction])
        self.mock_client.get_categories = AsyncMock(return_value={})
        self.mock_client.get_accounts = AsyncMock(return_value={})

        async def run_test():
            result = await self.tool.execute(
                self.mock_client, {"transaction_id": "geo-transaction"}
            )
            content = result.content[0].text

            self.assertIn("Местоположение", content)
            self.assertIn("55.7558, 37.6176", content)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
