"""
# Service transaction module

This module provides the `TransactionService` class, which is responsible for managing transactions
within a budget in the YNAB (You Need A Budget) system. The service includes methods to retrieve,
create, update, and delete transactions, as well as to retrieve transactions by account, category,
payee, and month.

Classes:
    TransactionService: A service class for managing transactions in a YNAB budget.
"""

from datetime import date
from typing import Any
from uuid import UUID

from uynab.model.transaction import (
    NewTransaction,
    ResponseSaveTransactions,
    ResponseTransaction,
    ResponseTransactions,
    SaveTransactionWithIdOrImportId,
    TransactionDetail,
)
from uynab.service.service import YNABService


class TransactionService(YNABService):
    def get_all_transactions(
        self,
        budget_id: UUID,
        since_date: date | None = None,
        last_knowledge_of_server: int | None = None,
    ) -> list[TransactionDetail]:
        """
        Retrieve all transactions for a given budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            since_date (date, optional): The date from which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int, optional): The last knowledge of the server. Defaults to None.

        Returns:
            list[TransactionDetail]: A list of transactions associated with the budget.
        """
        params = self._prepare_params(since_date, last_knowledge_of_server)
        response = self.perform_api_call(
            ResponseTransactions,
            "GET",
            f"budgets/{budget_id}/transactions",
            params=params or None,
        )
        return response.data.transactions

    def get_transaction(
        self, budget_id: UUID, transaction_id: UUID
    ) -> TransactionDetail:
        """
        Retrieve a specific transaction from a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            transaction_id (UUID): The unique identifier of the transaction.

        Returns:
            TransactionDetail: The transaction object retrieved from the budget.
        """
        response = self.perform_api_call(
            ResponseTransaction,
            "GET",
            f"budgets/{budget_id}/transactions/{transaction_id}",
        )
        return response.data.transaction

    def create_transactions(
        self, budget_id: UUID, transactions: list[NewTransaction]
    ) -> list[TransactionDetail]:
        """
        Create new transactions in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            transactions (NewTransaction): The transaction object to be created.

        Returns:
            TransactionDetail: The created transaction object.
        """
        data: dict[str, list[str]] = {"transactions": []}
        for transaction in transactions:
            data["transactions"].append(transaction.model_dump_json())

        response = self.perform_api_call(
            ResponseTransactions,
            "POST",
            f"budgets/{budget_id}/transactions",
            data=data,
        )
        return response.data.transactions

    def update_transactions(
        self, budget_id: UUID, transactions: list[SaveTransactionWithIdOrImportId]
    ) -> list[TransactionDetail]:
        """
        Updates a list of transactions for a given budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            transactions (list[SaveTransactionWithIdOrImportId]): A list of transactions to be updated.

        Returns:
            list[TransactionDetail]: A list of updated transaction details.
        """
        data: dict[str, list[str]] = {"transactions": []}
        for transaction in transactions:
            data["transactions"].append(transaction.model_dump_json())

        response = self.perform_api_call(
            ResponseSaveTransactions,
            "PUT",
            f"budgets/{budget_id}/transactions",
            data=data,
        )
        return response.data.transactions

    def update_transaction(
        self, budget_id: UUID, transaction_id: str, transaction: NewTransaction
    ) -> TransactionDetail:
        """
        Update existing transactions in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            transaction_id (str): The unique identifier of the transaction.
            transaction (NewTransaction): The transaction object with updated data.

        Returns:
            Transaction: The updated transaction object.
        """
        data: dict[str, str] = {"transaction": transaction.model_dump_json()}

        response = self.perform_api_call(
            ResponseTransaction,
            "PATCH",
            f"budgets/{budget_id}/transactions/{transaction_id}",
            data=data,
        )
        return response.data.transaction

    def delete_transaction(
        self, budget_id: UUID, transaction_id: UUID
    ) -> TransactionDetail:
        """
        Delete a specific transaction from a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            transaction_id (UUID): The unique identifier of the transaction.
        """
        response = self.perform_api_call(
            ResponseTransaction,
            "DELETE",
            f"budgets/{budget_id}/transactions/{transaction_id}",
        )

        return response.data.transaction

    def get_transactions_by_account(
        self,
        budget_id: UUID,
        account_id: UUID,
        since_date: date | None = None,
        last_knowledge_of_server: int | None = None,
    ) -> list[TransactionDetail]:
        """
        Retrieve all transactions for a specific account in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            account_id (UUID): The unique identifier of the account.
            since_date (date, optional): The date from which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int, optional): The last knowledge of the server. Defaults to None.

        Returns:
            list[TransactionDetail]: A list of transactions associated with the account.
        """
        params = self._prepare_params(since_date, last_knowledge_of_server)
        response = self.perform_api_call(
            ResponseTransactions,
            "GET",
            f"budgets/{budget_id}/accounts/{account_id}/transactions",
            params=params or None,
        )
        return response.data.transactions

    def get_transactions_by_category(
        self,
        budget_id: UUID,
        category_id: UUID,
        since_date: date | None = None,
        last_knowledge_of_server: int | None = None,
    ) -> list[TransactionDetail]:
        """
        Retrieve all transactions for a specific category in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            category_id (UUID): The unique identifier of the category.
            since_date (date, optional): The date from which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int, optional): The last knowledge of the server. Defaults to None.

        Returns:
            list[TransactionDetail]: A list of transactions associated with the category.
        """
        params = self._prepare_params(since_date, last_knowledge_of_server)
        response = self.perform_api_call(
            ResponseTransactions,
            "GET",
            f"budgets/{budget_id}/categories/{category_id}/transactions",
            params=params or None,
        )
        return response.data.transactions

    def get_transactions_by_payee(
        self,
        budget_id: UUID,
        payee_id: UUID,
        since_date: date | None = None,
        last_knowledge_of_server: int | None = None,
    ) -> list[TransactionDetail]:
        """
        Retrieve all transactions for a specific payee in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            payee_id (UUID): The unique identifier of the payee.
            since_date (date, optional): The date from which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int, optional): The last knowledge of the server. Defaults to None.

        Returns:
            list[TransactionDetail]: A list of transactions associated with the payee.
        """
        params = self._prepare_params(since_date, last_knowledge_of_server)
        response = self.perform_api_call(
            ResponseTransactions,
            "GET",
            f"budgets/{budget_id}/payees/{payee_id}/transactions",
            params=params or None,
        )
        return response.data.transactions

    def get_transactions_by_month(
        self,
        budget_id: UUID,
        month: date,
        since_date: date | None = None,
        last_knowledge_of_server: int | None = None,
    ) -> list[TransactionDetail]:
        """
        Retrieve all transactions for a specific month in a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            month (date): The budget month for which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01)
            since_date (date, optional): The date from which to retrieve transactions.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int, optional): The last knowledge of the server. Defaults to None.

        Returns:
            list[TransactionDetail]: A list of transactions associated with the month.
        """
        params = self._prepare_params(since_date, last_knowledge_of_server)
        response = self.perform_api_call(
            ResponseTransactions,
            "GET",
            f"budgets/{budget_id}/months/{month}/transactions",
            params=params or None,
        )
        return response.data.transactions

    @staticmethod
    def _prepare_params(
        since_date: date | None, last_knowledge_of_server: int | None
    ) -> dict[str, Any]:
        """
        Prepare a dictionary of parameters for a request.

        Args:
            since_date (date | None): The starting date for the request.
                If provided, it will be converted to a string.
                ISO formatted (e.g. 2024-01-01). Defaults to None.
            last_knowledge_of_server (int | None): The last known server state.
                If provided, it will be included as is. Defaults to None.

        Returns:
            dict: A dictionary containing the prepared parameters.
        """
        params: dict[str, str | int] = {}
        if since_date:
            params["since_date"] = str(since_date)
        if last_knowledge_of_server:
            params["last_knowledge_of_server"] = last_knowledge_of_server
        return params
