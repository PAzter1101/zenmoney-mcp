"""
Инициализация модуля отчетов
"""

from .cash_flow import CashFlowReport
from .category import CategoryBreakdownReport
from .income import IncomeAnalysisReport
from .merchant import MerchantAnalysisReport
from .spending import SpendingReport

__all__ = [
    "SpendingReport",
    "CategoryBreakdownReport",
    "MerchantAnalysisReport",
    "IncomeAnalysisReport",
    "CashFlowReport",
]
