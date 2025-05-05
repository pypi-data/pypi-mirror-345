"""
# Service account module

This module provides the AccountService class for interacting with accounts in the YNAB (You Need A Budget) API.

Classes:
    AccountService: A service class for performing operations related to accounts in a YNAB budget.
"""

from uuid import UUID

from uynab.model.account import (
    Account,
    RequestDataAccount,
    ResponseAccount,
    ResponseAccounts,
)
from uynab.service.service import YNABService


class AccountService(YNABService):
    def get_all_accounts(self, budget_id: UUID) -> list[Account]:
        response = self.perform_api_call(
            ResponseAccounts, "GET", f"budgets/{budget_id}/accounts"
        )
        return response.data.accounts

    def get_account(self, budget_id: UUID, account_id: UUID) -> Account:
        response = self.perform_api_call(
            ResponseAccount, "GET", f"budgets/{budget_id}/accounts/{account_id}"
        )
        return response.data.account

    def create_account(self, budget_id: UUID, data: dict) -> Account:
        response = self.perform_api_call(
            ResponseAccount,
            "POST",
            f"budgets/{budget_id}/accounts",
            data=RequestDataAccount(**data).model_dump_json(),
        )
        return response.data.account

    # Not standard methods

    def _get_account_by_name(self, budget_id: UUID, account_name: str) -> Account:
        all_accounts = self.get_all_accounts(budget_id)
        for account in all_accounts:
            if account.name == account_name:
                return account
        raise ValueError(f"Account '{account_name}' not found")

    def _get_account_id(self, budget_id: UUID, account_name: str) -> UUID:
        account = self._get_account_by_name(budget_id, account_name)
        return account.id
