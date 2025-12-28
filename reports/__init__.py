"""
Инициализация модуля отчетов
"""

from .spending import SpendingReport
from .category import CategoryBreakdownReport
from .merchant import MerchantAnalysisReport
from .income import IncomeAnalysisReport
from .cash_flow import CashFlowReport

__all__ = ['SpendingReport', 'CategoryBreakdownReport', 'MerchantAnalysisReport', 'IncomeAnalysisReport', 'CashFlowReport']
