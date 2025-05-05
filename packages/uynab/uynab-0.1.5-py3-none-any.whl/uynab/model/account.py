"""
# Model account module

This module defines the data models for representing financial accounts and their related responses and requests.

Classes:
    Account: Represents a financial account with various attributes such as id, name, type, balance, etc.
    ResponseDataAccount: Represents the response data for a single account.
    ResponseAccount: Represents the response for a single account.
    ResponseDataAccounts: Represents the response data for a list of accounts.
    ResponseAccounts: Represents the response for a list of accounts.
    RequestAccount: Represents the request data for creating or updating an account.
    RequestDataAccount: Represents the request data wrapper for an account.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Account(BaseModel):
    """
    Account model representing a financial account.

    Attributes:
        id (UUID): Unique identifier for the account.
        name (str): Name of the account.
        type (str): Type of the account (e.g., checking, savings).
        on_budget (bool): Indicates if the account is on budget.
        closed (bool): Indicates if the account is closed.
        note (Optional[str]): Additional notes about the account.
        balance (int): Current balance of the account.
        cleared_balance (int): Cleared balance of the account.
        uncleared_balance (int): Uncleared balance of the account.
        transfer_payee_id (UUID): Identifier for the transfer payee.
        direct_import_linked (bool): Indicates if the account is linked for direct import.
        direct_import_in_error (bool): Indicates if there is an error with direct import.
        last_reconciled_at (Optional[str]): Timestamp of the last reconciliation.
        debt_original_balance (Optional[int]): Original balance of the debt.
        debt_interest_rates (dict[datetime, int]): Interest rates of the debt over time.
        debt_minimum_payments (dict[datetime, int]): Minimum payments of the debt over time.
        debt_escrow_amounts (dict[datetime, int]): Escrow amounts of the debt over time.
        deleted (bool): Indicates if the account is deleted.
    """

    id: UUID
    name: str
    type: str
    on_budget: bool
    closed: bool
    note: Optional[str] = None
    balance: int
    cleared_balance: int
    uncleared_balance: int
    transfer_payee_id: UUID
    direct_import_linked: bool
    direct_import_in_error: bool
    last_reconciled_at: Optional[str] = None
    debt_original_balance: Optional[int] = None
    debt_interest_rates: dict[datetime, int]
    debt_minimum_payments: dict[datetime, int]
    debt_escrow_amounts: dict[datetime, int]
    deleted: bool


class ResponseDataAccount(BaseModel):
    """ResponseDataAccount is a model representing the response data for an account."""

    account: Account


class ResponseAccount(BaseModel):
    """ResponseAccount is a model representing the response for an account."""

    data: ResponseDataAccount


class ResponseDataAccounts(BaseModel):
    """ResponseDataAccounts is a model representing the response data for a list of accounts."""

    accounts: list[Account]
    server_knowledge: int


class ResponseAccounts(BaseModel):
    """ResponseAccounts is a model representing the response for a list of accounts."""

    data: ResponseDataAccounts


class RequestAccount(BaseModel):
    """
    RequestAccount model representing an account request.
    Attributes:
        name (str): The name of the account.
        type (str): The type of the account.
        balance (int): The balance of the account.
    """

    name: str
    type: str
    balance: int


class RequestDataAccount(BaseModel):
    """
    RequestDataAccount is a data model that represents the request data for an account.

    Attributes:
        account (RequestAccount): An instance of RequestAccount containing the account details.
    """

    account: RequestAccount
