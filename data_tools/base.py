"""
Базовый класс для инструментов данных
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from mcp.types import CallToolResult
from src.client import ZenMoneyClient

class BaseDataTool(ABC):
    """Базовый класс для всех инструментов данных"""
    
    @abstractmethod
    async def execute(self, client: ZenMoneyClient, args: Dict[str, Any]) -> CallToolResult:
        """Выполнение инструмента"""
        pass
