"""
Юнит-тесты для модели Transaction
"""

import unittest
from models.transaction import Transaction


class TestTransactionModel(unittest.TestCase):
    """Тесты для модели Transaction"""
    
    def test_basic_transaction_creation(self):
        """Тест создания базовой транзакции"""
        t = Transaction(
            id="test-123",
            date="2025-01-01",
            income=100.0,
            outcome=0.0
        )
        
        self.assertEqual(t.id, "test-123")
        self.assertEqual(t.date, "2025-01-01")
        self.assertEqual(t.income, 100.0)
        self.assertEqual(t.outcome, 0.0)
        self.assertEqual(t.amount, 100.0)
    
    def test_transaction_with_qr_code(self):
        """Тест транзакции с QR-кодом чека"""
        qr_code = "t=20250915T1918&s=470.00&fn=7380440902332634&i=105519&fp=231257316&n=1"
        
        t = Transaction(
            id="samokat-transaction",
            date="2025-09-15",
            outcome=470.0,
            payee="SBER*5411*SAMOKAT",
            qrCode=qr_code
        )
        
        self.assertEqual(t.qrCode, qr_code)
        self.assertEqual(t.payee, "SBER*5411*SAMOKAT")
        self.assertEqual(t.amount, -470.0)
    
    def test_transaction_properties(self):
        """Тест свойств транзакции (доход/расход/перевод)"""
        # Расход
        expense = Transaction(
            id="expense",
            date="2025-01-01",
            outcome=100.0
        )
        self.assertTrue(expense.is_expense)
        self.assertFalse(expense.is_income)
        self.assertFalse(expense.is_transfer)
        
        # Доход
        income = Transaction(
            id="income",
            date="2025-01-01",
            income=100.0
        )
        self.assertTrue(income.is_income)
        self.assertFalse(income.is_expense)
        self.assertFalse(income.is_transfer)
        
        # Перевод между счетами
        transfer = Transaction(
            id="transfer",
            date="2025-01-01",
            income=100.0,
            outcome=100.0,
            incomeAccount="account-1",
            outcomeAccount="account-2"
        )
        self.assertTrue(transfer.is_transfer)
        self.assertFalse(transfer.is_income)
        self.assertFalse(transfer.is_expense)
    
    def test_transaction_with_geolocation(self):
        """Тест транзакции с геолокацией"""
        t = Transaction(
            id="geo-transaction",
            date="2025-01-01",
            outcome=500.0,
            latitude=55.7558,
            longitude=37.6176
        )
        
        self.assertEqual(t.latitude, 55.7558)
        self.assertEqual(t.longitude, 37.6176)
    
    def test_transaction_with_tags(self):
        """Тест транзакции с тегами"""
        t = Transaction(
            id="tagged-transaction",
            date="2025-01-01",
            outcome=300.0,
            tag=["category-1", "category-2"]
        )
        
        self.assertEqual(t.tag, ["category-1", "category-2"])


if __name__ == '__main__':
    unittest.main()
