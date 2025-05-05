import os
from uuid import UUID

import pytest
from dotenv import load_dotenv

from uynab.client import YNABClient
from uynab.model.account import Account
from uynab.model.category import CategoryGroup
from uynab.model.payee import Payee
from uynab.model.transaction import TransactionDetail
from uynab.service.account import AccountService
from uynab.service.budget import BudgetService
from uynab.service.category import CategoryService
from uynab.service.payee import PayeeService
from uynab.service.transaction import TransactionService


@pytest.fixture
def client():
    load_dotenv()
    token = os.getenv("YNAB_API_TOKEN")
    return YNABClient(api_token=token)


@pytest.fixture
def budget_id(client):
    return os.getenv("BUDGET_ID")


@pytest.mark.slow
def test_account(client, budget_id):
    account_service = AccountService(client=client)
    account = account_service.get_all_accounts(budget_id=budget_id)
    assert account is not None
    assert isinstance(account[0], Account)


@pytest.mark.slow
def test_budget_service(client, budget_id):
    budget_service = BudgetService(client=client)
    budget_id = budget_service._get_budget_id("Familly")
    assert budget_id is not None
    assert isinstance(budget_id, UUID)


@pytest.mark.slow
def test_payee_service(client, budget_id):
    payee_service = PayeeService(client=client)
    payees = payee_service.get_all_payees(budget_id=budget_id)
    assert payees is not None
    assert isinstance(payees[0], Payee)


@pytest.mark.slow
def test_category_service(client, budget_id):
    category_service = CategoryService(client=client)
    categories = category_service.get_all_categories(budget_id=budget_id)
    assert categories is not None
    assert isinstance(categories[0], CategoryGroup)


@pytest.mark.slow
def test_transaction(client, budget_id):
    transaction_service = TransactionService(client=client)
    transactions = transaction_service.get_all_transactions(budget_id=budget_id)
    assert transactions is not None
    assert isinstance(transactions[0], TransactionDetail)
