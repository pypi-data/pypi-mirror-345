"""
# Model transaction module

This module defines various Pydantic models for representing financial transactions and their related data.

Classes:
    Subtransaction: Represents a subtransaction within a transaction.
    SaveSubTransaction: Represents a sub-transaction to be saved.
    TransactionDetail: Represents the details of a financial transaction.
    TransactionSummary: Represents a summary of a financial transaction.
    NewTransaction: Represents a new financial transaction.
    ResponseDataTransaction: Represents the response data for a transaction.
    ResponseTransaction: Represents a transaction response.
    ResponseDataTransactions: Represents the response data for multiple transactions.
    ResponseTransactions: Represents the response containing transaction data.
    ResponseDataSaveTransactions: Represents the response data for saving transactions.
    ResponseSaveTransactions: Represents the response received after saving transactions.
"""

from datetime import date
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from uynab.model.utils import FlagColor


class Subtransaction(BaseModel):
    """
    Represents a subtransaction within a transaction.

    Attributes:
        id (UUID): Unique identifier for the subtransaction.
        transaction_id (UUID): Unique identifier for the parent transaction.
        amount (int): The amount of the subtransaction.
        memo (Optional[str]): An optional memo for the subtransaction.
        payee_id (Optional[UUID]): Optional unique identifier for the payee.
        payee_name (Optional[str]): Optional name of the payee.
        category_id (Optional[UUID]): Optional unique identifier for the category.
        category_name (Optional[str]): Optional name of the category.
        transfer_account_id (Optional[UUID]): Optional unique identifier for the transfer account.
        transfer_transaction_id (Optional[UUID]): Optional unique identifier for the transfer transaction.
        deleted (bool): Indicates whether the subtransaction is deleted.
    """

    id: UUID
    transaction_id: UUID
    amount: int
    memo: Optional[str] = None
    payee_id: Optional[UUID] = None
    payee_name: Optional[str] = None
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    transfer_account_id: Optional[UUID] = None
    transfer_transaction_id: Optional[UUID] = None
    deleted: bool


class SaveSubTransaction(BaseModel):
    """
    Represents a sub-transaction to be saved.

    Attributes:
        amount (int): The amount of the sub-transaction.
        payee_id (Optional[UUID]): The ID of the payee associated with the sub-transaction.
        payee_name (Optional[str]): The name of the payee associated with the sub-transaction.
        category_id (Optional[UUID]): The ID of the category associated with the sub-transaction.
        memo (Optional[str]): An optional memo for the sub-transaction.
    """

    amount: int
    payee_id: Optional[UUID] = None
    payee_name: Optional[str] = None
    category_id: Optional[UUID] = None
    memo: Optional[str] = None


class TransactionDetail(BaseModel):
    """
    TransactionDetail represents the details of a financial transaction.

    Attributes:
        id (str): Unique identifier for the transaction.
        date (date): The date of the transaction.
        amount (int): The amount of the transaction in the smallest currency unit (e.g., cents).
        memo (Optional[str]): A memo or note associated with the transaction.
        cleared (Literal["cleared", "uncleared", "reconciled"]): The cleared status of the transaction.
        approved (bool): Indicates whether the transaction is approved.
        flag_color (Optional[FlagColor]): The color of the flag associated with the transaction.
        flag_name (Optional[str]): The name of the flag associated with the transaction.
        account_id (UUID): The unique identifier of the account associated with the transaction.
        payee_id (Optional[UUID]): The unique identifier of the payee associated with the transaction.
        category_id (Optional[UUID]): The unique identifier of the category associated with the transaction.
        transfer_account_id (Optional[UUID]): The unique identifier of the transfer account associated with the transaction.
        transfer_transaction_id (Optional[str]): The unique identifier of the transfer transaction associated with the transaction.
        matched_transaction_id (Optional[str]): The unique identifier of the matched transaction associated with the transaction.
        import_id (Optional[UUID]): The unique identifier of the import associated with the transaction.
        import_payee_name (Optional[str]): The name of the payee as imported.
        import_payee_name_original (Optional[str]): The original name of the payee as imported.
        debt_transaction_type (Optional[str]): The type of debt transaction.
        deleted (bool): Indicates whether the transaction is deleted.
        account_name (str): The name of the account associated with the transaction.
        payee_name (Optional[str]): The name of the payee associated with the transaction.
        category_name (Optional[str]): The name of the category associated with the transaction.
        subtransactions (list[Subtransaction]): A list of subtransactions associated with the transaction.
    """

    id: str
    date: date
    amount: int
    memo: Optional[str] = None
    cleared: Literal["cleared", "uncleared", "reconciled"]
    approved: bool
    flag_color: Optional[FlagColor] = None
    flag_name: Optional[str] = None
    account_id: UUID
    payee_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    transfer_account_id: Optional[UUID] = None
    transfer_transaction_id: Optional[str] = None
    matched_transaction_id: Optional[str] = None
    import_id: Optional[UUID] = None
    import_payee_name: Optional[str] = None
    import_payee_name_original: Optional[str] = None
    debt_transaction_type: Optional[str] = None
    deleted: bool
    account_name: str
    payee_name: Optional[str] = None
    category_name: Optional[str] = None
    subtransactions: list[Subtransaction]


class TransactionSummary(BaseModel):
    """
    TransactionSummary represents a summary of a financial transaction.

    Attributes:
        id (str): Unique identifier for the transaction.
        date (date): The date of the transaction.
        amount (int): The amount of the transaction in the smallest currency unit (e.g., cents).
        memo (Optional[str]): A memo or note associated with the transaction.
        cleared (Literal["cleared", "uncleared", "reconciled"]): The cleared status of the transaction.
        approved (bool): Indicates whether the transaction is approved.
        flag_color (Optional[FlagColor]): The color of the flag associated with the transaction.
        flag_name (Optional[str]): The name of the flag associated with the transaction.
        account_id (UUID): The unique identifier of the account associated with the transaction.
        payee_id (Optional[UUID]): The unique identifier of the payee associated with the transaction.
        category_id (Optional[UUID]): The unique identifier of the category associated with the transaction.
        transfer_account_id (Optional[UUID]): The unique identifier of the transfer account associated with the transaction.
        transfer_transaction_id (Optional[str]): The unique identifier of the transfer transaction associated with the transaction.
        matched_transaction_id (Optional[str]): The unique identifier of the matched transaction.
        import_id (Optional[UUID]): The unique identifier of the import associated with the transaction.
        import_payee_name (Optional[str]): The name of the payee as imported.
        import_payee_name_original (Optional[str]): The original name of the payee as imported.
        debt_transaction_type (Optional[str]): The type of debt transaction.
        deleted (bool): Indicates whether the transaction is deleted.
    """

    id: str
    date: date
    amount: int
    memo: Optional[str] = None
    cleared: Literal["cleared", "uncleared", "reconciled"]
    approved: bool
    flag_color: Optional[FlagColor] = None
    flag_name: Optional[str] = None
    account_id: UUID
    payee_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    transfer_account_id: Optional[UUID] = None
    transfer_transaction_id: Optional[str] = None
    matched_transaction_id: Optional[str] = None
    import_id: Optional[UUID] = None
    import_payee_name: Optional[str] = None
    import_payee_name_original: Optional[str] = None
    debt_transaction_type: Optional[str] = None
    deleted: bool


class NewTransaction(BaseModel):
    """
    NewTransaction model representing a financial transaction.

    Attributes:
        account_id (UUID): The unique identifier for the account.
        date (date): The date of the transaction.
        amount (int): The amount of the transaction in the smallest currency unit (e.g., cents).
        payee_id (Optional[UUID]): The unique identifier for the payee (optional).
        payee_name (Optional[str]): The name of the payee (optional).
        category_id (Optional[UUID]): The unique identifier for the category (optional).
        memo (Optional[str]): A memo or note associated with the transaction (optional).
        cleared (Literal["cleared", "uncleared", "reconciled"]): The cleared status of the transaction.
        approved (bool): Whether the transaction is approved.
        flag_color (Optional[str]): The color of the flag associated with the transaction (optional).
        import_id (Optional[str]): The import identifier for the transaction (optional).
        subtransactions (list[SaveSubTransaction]): A list of subtransactions associated with this transaction.
    """

    account_id: UUID
    date: date
    amount: int
    payee_id: Optional[UUID] = None
    payee_name: Optional[str] = None
    category_id: Optional[UUID] = None
    memo: Optional[str] = None
    cleared: Literal["cleared", "uncleared", "reconciled"]
    approved: bool
    flag_color: Optional[FlagColor] = None
    import_id: Optional[str] = None
    subtransactions: list[SaveSubTransaction]


class SaveTransactionWithIdOrImportId(BaseModel):
    id: Optional[str] = None
    import_id: Optional[str] = None
    account_id: UUID
    date: date
    amount: int
    payee_id: Optional[UUID] = None
    payee_name: Optional[str] = None
    category_id: Optional[UUID] = None
    memo: Optional[str] = None
    cleared: Literal["cleared", "uncleared", "reconciled"]
    approved: bool
    flag_color: Optional[FlagColor] = None
    subtransactions: list[SaveSubTransaction]


class ResponseDataTransaction(BaseModel):
    """
    ResponseDataTransaction is a model that represents the response data for a transaction.

    Attributes:
        transaction (TransactionDetail): Detailed information about the transaction.
    """

    transaction: TransactionDetail


class ResponseTransaction(BaseModel):
    """
    ResponseTransaction is a model representing a transaction response.

    Attributes:
        data (ResponseDataTransaction): The data associated with the transaction response.
    """

    data: ResponseDataTransaction


class ResponseDataTransactions(BaseModel):
    """
    ResponseDataTransactions is a model representing the response data for transactions.

    Attributes:
        transactions (list[TransactionDetail]): A list of transaction details.
        server_knowledge (int): An integer representing the server's knowledge of the current state.
    """

    transactions: list[TransactionDetail]
    server_knowledge: int


class ResponseTransactions(BaseModel):
    """
    ResponseTransactions is a model that represents the response containing transaction data.

    Attributes:
        data (ResponseDataTransactions): The transaction data included in the response.
    """

    data: ResponseDataTransactions


class ResponseDataSaveTransactions(BaseModel):
    """
    ResponseDataSaveTransactions is a model representing the response data for saving transactions.

    Attributes:
        transaction_ids (list[str]): A list of transaction IDs.
        transactions (list[TransactionDetail]): A list of transaction details.
        duplicate_import_ids (list[str]): A list of duplicate import IDs.
        server_knowledge (int): The server knowledge value.
    """

    transaction_ids: list[str]
    transactions: list[TransactionDetail]
    duplicate_import_ids: list[str]
    server_knowledge: int


class ResponseSaveTransactions(BaseModel):
    """
    ResponseSaveTransactions is a model representing the response received after saving transactions.

    Attributes:
        data (ResponseDataSaveTransactions): The data related to the saved transactions.
    """

    data: ResponseDataSaveTransactions
