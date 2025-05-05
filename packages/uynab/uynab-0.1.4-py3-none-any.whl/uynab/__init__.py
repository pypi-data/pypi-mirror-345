"""Micro YNAB - a small SDK for YNAB API"""

from importlib.metadata import version

from uynab.client import YNABClient
from uynab.service.budget import BudgetService
from uynab.service.category import CategoryService
from uynab.service.payee import PayeeService
from uynab.service.transaction import TransactionService

__version__ = version("uynab")

__all__ = [
    "YNABClient",
    "BudgetService",
    "CategoryService",
    "PayeeService",
    "TransactionService",
]
