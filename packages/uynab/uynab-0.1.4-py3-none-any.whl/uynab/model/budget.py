"""
# Model budget module.

This module defines the models related to budgets in the application using Pydantic BaseModel.

Classes:
    Budget: Represents a budget with various attributes such as accounts, payees, categories, and transactions.
    ResponseDataBudget: Represents the response data for a single budget.
    ResponseBudget: Represents the response structure for a single budget.
    ResponseDataBudgets: Represents the response data for multiple budgets.
    ResponseBudgets: Represents the response structure for multiple budgets.
    BudgetSettings: Represents the settings for a budget, including date and currency formats.
    ResponseDataBudgetSettings: Represents the response data for budget settings.
    ResponseBudgetSettings: Represents the response structure for budget settings.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from uynab.model.account import Account
from uynab.model.category import Category, CategoryGroup
from uynab.model.payee import Payee
from uynab.model.transaction import Subtransaction, TransactionSummary
from uynab.model.utils import CurrencyFormat, DateFormat, Month


class Budget(BaseModel):
    """
    A class representing a budget in the application.

    Attributes:
        id (UUID): The unique identifier of the budget.
        name (str): The name of the budget.
        last_modified_on (datetime): The date and time when the budget was last modified.
        first_month (datetime): The first month of the budget.
        last_month (datetime): The last month of the budget.
        date_format (DateFormat): The date format used in the budget.
        currency_format (CurrencyFormat): The currency format used in the budget.
        accounts (list[Account]): A list of accounts associated with the budget.
        payees (list[Payee]): A list of payees associated with the budget.
        payee_locations (list[dict]): A list of payee locations associated with the budget.
        category_groups (list[CategoryGroup]): A list of category groups in the budget.
        categories (list[Category]): A list of categories in the budget.
        months (list[Month]): A list of months in the budget.
        transactions (list[TransactionSummary]): A list of transactions in the budget.
        subtransactions (list[Subtransaction]): A list of subtransactions in the budget.
        scheduled_transactions (list[dict]): A list of scheduled transactions in the budget.
        scheduled_subtransactions (list[dict]): A list of scheduled subtransactions in the budget.
    """

    id: UUID
    name: str
    last_modified_on: datetime
    first_month: datetime
    last_month: datetime
    date_format: DateFormat
    currency_format: CurrencyFormat
    accounts: list[Account]
    payees: list[Payee]
    payee_locations: list[dict]
    category_groups: list[CategoryGroup]
    categories: list[Category]
    months: list[Month]
    transactions: list[TransactionSummary]
    subtransactions: list[Subtransaction]
    scheduled_transactions: list[dict]
    scheduled_subtransactions: list[dict]


class BudgetSummary(BaseModel):
    """
    BudgetSummary model representing a summary of a budget.
    Attributes:
        id (UUID): Unique identifier for the budget.
        name (str): Name of the budget.
        last_modified_on (datetime): Timestamp of the last modification.
        first_month (datetime): The first month of the budget.
        last_month (datetime): The last month of the budget.
        date_format (Optional[DateFormat]): The date format used in the budget.
        currency_format (Optional[CurrencyFormat]): The currency format used in the budget.
    """

    id: UUID
    name: str
    last_modified_on: datetime
    first_month: datetime
    last_month: datetime
    date_format: Optional[DateFormat] = None
    currency_format: Optional[CurrencyFormat] = None


class ResponseDataBudget(BaseModel):
    """
    ResponseDataBudget is a model representing the response data for a budget.

    Attributes:
        budget (Budget): The budget data.
        server_knowledge (int): The server knowledge value.
    """

    budget: Budget
    server_knowledge: int


class ResponseBudget(BaseModel):
    """
    ResponseBudget is a model representing the response structure for a budget.

    Attributes:
        data (ResponseDataBudget): The data attribute containing the budget details.
    """

    data: ResponseDataBudget


class ResponseDataBudgets(BaseModel):
    """
    ResponseDataBudgets is a model representing the response data for budgets.

    Attributes:
        budgets (list[BudgetSummary]): A list of Budget objects.
        default_budget (Optional[BudgetSummary]): The default Budget object.
    """

    budgets: list[BudgetSummary]
    default_budget: Optional[BudgetSummary] = None


class ResponseBudgets(BaseModel):
    """
    ResponseBudgets is a model representing the response structure for budget-related data.

    Attributes:
        data (ResponseDataBudgets): The data attribute containing budget-related information.
    """

    data: ResponseDataBudgets


class BudgetSettings(BaseModel):
    """A class used to represent the settings for a budget.

    Attributes:
        date_format (dict): A dictionary representing the format for dates.
        currency_format (dict): A dictionary representing the format for currency.
    """

    date_format: DateFormat
    currency_format: CurrencyFormat


class ResponseDataBudgetSettings(BaseModel):
    """
    ResponseDataBudgetSettings is a model representing the settings of a budget response.

    Attributes:
        settings (BudgetSettings): The settings of the budget.
    """

    settings: BudgetSettings


class ResponseBudgetSettings(BaseModel):
    """
    ResponseBudgetSettings is a model representing the settings of a budget response.

    Attributes:
        data (ResponseDataBudgetSettings): The data containing the budget settings.
    """

    data: ResponseDataBudgetSettings
