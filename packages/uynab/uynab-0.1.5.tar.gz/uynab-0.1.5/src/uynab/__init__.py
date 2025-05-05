"""Micro YNAB - a small SDK for YNAB API"""

from importlib.metadata import version

from uynab import model
from uynab.client import YNABClient
from uynab.service.account import AccountService
from uynab.service.budget import BudgetService
from uynab.service.category import CategoryService
from uynab.service.payee import PayeeService
from uynab.service.transaction import TransactionService

__version__ = version("uynab")

__all__ = [
    "model",
    "YNABClient",
    "AccountService",
    "BudgetService",
    "CategoryService",
    "PayeeService",
    "TransactionService",
]
