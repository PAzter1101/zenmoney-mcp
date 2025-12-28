"""
API клиент для ДзенМани
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from models.account import Account
from models.category import Category
from models.transaction import Transaction


class ZenMoneyClient:
    """Клиент для работы с API ДзенМани"""

    def __init__(self, token: str, base_url: str = "https://api.zenmoney.ru"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_data(self) -> Dict[str, Any]:
        """Получение всех данных через diff API"""
        url = f"{self.base_url}/v8/diff/"
        payload = {
            "serverTimestamp": 0,
            "currentClientTimestamp": int(datetime.now().timestamp()),
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result

    async def get_transactions(self) -> List[Transaction]:
        """Получение всех транзакций"""
        data = await self.get_data()
        transactions = []

        for t_data in data.get("transaction", []):
            transactions.append(Transaction(**t_data))

        return transactions

    async def get_categories(self) -> Dict[str, Category]:
        """Получение всех категорий"""
        data = await self.get_data()
        categories = {}

        for c_data in data.get("tag", []):
            categories[c_data["id"]] = Category(**c_data)

        return categories

    async def get_accounts(self) -> Dict[str, Account]:
        """Получение всех счетов"""
        data = await self.get_data()
        accounts = {}

        for a_data in data.get("account", []):
            accounts[a_data["id"]] = Account(**a_data)

        return accounts

    async def update_transaction(self, transaction_id: str, updates: Dict[str, Any]) -> bool:
        """Обновление транзакции"""
        url = f"{self.base_url}/v8/diff/"
        
        # Получаем текущие данные транзакции
        data = await self.get_data()
        transaction_data = None
        
        for t_data in data.get("transaction", []):
            if t_data["id"] == transaction_id:
                transaction_data = t_data.copy()
                break
                
        if not transaction_data:
            return False
            
        # Применяем обновления
        transaction_data.update(updates)
        transaction_data["changed"] = int(datetime.now().timestamp())
        
        payload = {
            "serverTimestamp": data.get("serverTimestamp", 0),
            "currentClientTimestamp": int(datetime.now().timestamp()),
            "transaction": [transaction_data]
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return True
