"""
Базовый класс для отчетов
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from mcp.types import CallToolResult

from models.transaction import TransactionFilter
from src.client import ZenMoneyClient
from utils.filters import filter_transactions


class BaseReport(ABC):
    """Базовый класс для всех отчетов"""

    @abstractmethod
    async def generate(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Генерация отчета"""
        pass

    def _create_filter_params(self, args: Dict[str, Any]) -> TransactionFilter:
        """Создание параметров фильтрации из аргументов"""
        return TransactionFilter(
            year=args.get("year"),
            month=args.get("month"),
            day=args.get("day"),
            date_from=args.get("date_from"),
            date_to=args.get("date_to"),
        )

    def _get_period_description(self, args: Dict[str, Any]) -> str:
        """Получение описания периода для заголовка отчета"""
        if args.get("date_from") or args.get("date_to"):
            if args.get("date_from") and args.get("date_to"):
                return f"{args['date_from']} — {args['date_to']}"
            elif args.get("date_from"):
                return f"с {args['date_from']}"
            else:
                return f"до {args['date_to']}"
        elif args.get("year"):
            result = str(args["year"])
            if args.get("month"):
                result += f"-{args['month']:02d}"
                if args.get("day"):
                    result += f"-{args['day']:02d}"
            return result
        else:
            return "весь период"
