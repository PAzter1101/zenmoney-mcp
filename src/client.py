"""
API клиент для ДзенМани
"""

import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.transaction import Transaction
from models.category import Category
from models.account import Account

class ZenMoneyClient:
    """Клиент для работы с API ДзенМани"""
    
    def __init__(self, token: str, base_url: str = "https://api.zenmoney.ru"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def get_data(self) -> Dict[str, Any]:
        """Получение всех данных через diff API"""
        url = f"{self.base_url}/v8/diff/"
        payload = {
            "serverTimestamp": 0,
            "currentClientTimestamp": int(datetime.now().timestamp())
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    async def get_transactions(self) -> List[Transaction]:
        """Получение всех транзакций"""
        data = await self.get_data()
        transactions = []
        
        for t_data in data.get('transaction', []):
            transactions.append(Transaction(**t_data))
        
        return transactions
    
    async def get_categories(self) -> Dict[str, Category]:
        """Получение всех категорий"""
        data = await self.get_data()
        categories = {}
        
        for c_data in data.get('tag', []):
            categories[c_data['id']] = Category(**c_data)
        
        return categories
    
    async def get_accounts(self) -> Dict[str, Account]:
        """Получение всех счетов"""
        data = await self.get_data()
        accounts = {}
        
        for a_data in data.get('account', []):
            accounts[a_data['id']] = Account(**a_data)
        
        return accounts
