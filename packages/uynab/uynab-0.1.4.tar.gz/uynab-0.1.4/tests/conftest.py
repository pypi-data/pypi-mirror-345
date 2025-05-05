import uuid
from datetime import date
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from uynab.client import YNABClient
from uynab.model.category import Category, CategoryGroup
from uynab.model.payee import Payee
from uynab.model.utils import FlagColor


@pytest.fixture
def ynab_client():
    return YNABClient(
        api_token="test_token", base_url="https://api.youneedabudget.com/v1"
    )


@pytest.fixture
def mock_client():
    mock = MagicMock(spec=YNABClient)
    mock._verbose = False
    return mock


@pytest.fixture
def payee():
    payee_data = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Test Payee",
        "transfer_account_id": None,
        "deleted": False,
    }
    return Payee(**payee_data)


@pytest.fixture
def budget_id():
    return uuid.uuid4()


@pytest.fixture
def category_id():
    return UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")


@pytest.fixture
def category_data(category_id):
    return {
        "id": category_id,
        "category_group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "category_group_name": "Test  Category Group",
        "name": "Test Category",
        "hidden": True,
        "original_category_group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "note": "string",
        "budgeted": 0,
        "activity": 0,
        "balance": 0,
        "goal_type": "TB",
        "goal_needs_whole_amount": None,
        "goal_day": 0,
        "goal_cadence": 0,
        "goal_cadence_frequency": 0,
        "goal_creation_month": "2024-12-22",
        "goal_target": 0,
        "goal_target_month": "2024-12-22",
        "goal_percentage_complete": 0,
        "goal_months_to_budget": 0,
        "goal_under_funded": 0,
        "goal_overall_funded": 0,
        "goal_overall_left": 0,
        "deleted": True,
    }


@pytest.fixture
def category(category_data):
    return Category(**category_data)


@pytest.fixture
def category_group_id():
    return UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")


@pytest.fixture
def category_group_data(category_group_id, category_data):
    category = Category(**category_data)
    return {
        "id": category_group_id,
        "name": "Test Category Group",
        "hidden": True,
        "deleted": True,
        "categories": [category],
    }


@pytest.fixture
def category_group(category_group_data):
    return CategoryGroup(**category_group_data)


@pytest.fixture
def subtransaction_id():
    return UUID("8d267248-7a94-467f-a158-93d609f7adf6")


@pytest.fixture
def transaction_detail_id():
    return "a48fd37c-4619-414d-820f-48a67c779e05"


@pytest.fixture
def subtransaction_data(subtransaction_id):
    return {
        "id": subtransaction_id,
        "transaction_id": "9746a5cd-a3b7-43bc-8a2a-cf76614f2209",
        "amount": -16090,
        "memo": "test memo",
        "payee_id": None,
        "payee_name": "test payee",
        "category_id": "a874697b-2b32-4e66-a452-f3b9c6522c36",
        "category_name": "test category",
        "transfer_account_id": None,
        "transfer_transaction_id": None,
        "deleted": False,
    }


@pytest.fixture
def savesubtransaction_data():
    return {
        "amount": -16090,
        "payee_id": None,
        "payee_name": "test payee",
        "category_id": "a874697b-2b32-4e66-a452-f3b9c6522c36",
        "memo": "test memo",
    }


@pytest.fixture
def transaction_detail_data(subtransaction_data, transaction_detail_id):
    return {
        "id": transaction_detail_id,
        "date": date(2024, 12, 21),
        "amount": -81080,
        "memo": "test memo",
        "cleared": "cleared",
        "approved": True,
        "flag_color": FlagColor.GREEN,
        "flag_name": None,
        "account_id": "8d267248-7a94-467f-a158-93d609f7adf6",
        "payee_id": "ce09c739-503b-4953-b594-cffd35c2cebd",
        "category_id": "cb7d3a9a-392c-4826-bbee-e6448591f475",
        "transfer_account_id": None,
        "transfer_transaction_id": None,
        "matched_transaction_id": None,
        "import_id": None,
        "import_payee_name": None,
        "import_payee_name_original": None,
        "debt_transaction_type": None,
        "deleted": False,
        "account_name": "test account",
        "payee_name": "test payee",
        "category_name": "test category",
        "subtransactions": [subtransaction_data],
    }


@pytest.fixture
def transaction_summary_data(transaction_detail_id):
    return {
        "id": transaction_detail_id,
        "date": date(2024, 12, 21),
        "amount": -81080,
        "memo": "test memo",
        "cleared": "cleared",
        "approved": True,
        "flag_color": None,
        "account_id": "8d267248-7a94-467f-a158-93d609f7adf6",
        "payee_id": "ce09c739-503b-4953-b594-cffd35c2cebd",
        "category_id": "cb7d3a9a-392c-4826-bbee-e6448591f475",
        "transfer_account_id": None,
        "transfer_transaction_id": None,
        "matched_transaction_id": None,
        "import_id": None,
        "import_payee_name": None,
        "import_payee_name_original": None,
        "debt_transaction_type": None,
        "deleted": False,
    }


@pytest.fixture
def new_transaction_data(transaction_detail_id, subtransaction_data):
    return {
        "account_id": transaction_detail_id,
        "date": date(2024, 12, 21),
        "amount": -81080,
        "payee_id": "ce09c739-503b-4953-b594-cffd35c2cebd",
        "payee_name": "test payee",
        "category_id": "cb7d3a9a-392c-4826-bbee-e6448591f475",
        "memo": "test memo",
        "cleared": "cleared",
        "approved": True,
        "flag_color": None,
        "import_id": None,
        "subtransactions": [subtransaction_data],
    }


@pytest.fixture
def save_transaction_with_id_or_import_id_data(
    subtransaction_data, transaction_detail_id
):
    return {
        "id": transaction_detail_id,
        "import_id": None,
        "account_id": "8d267248-7a94-467f-a158-93d609f7adf6",
        "date": date(2024, 12, 21),
        "amount": -81080,
        "payee_id": "ce09c739-503b-4953-b594-cffd35c2cebd",
        "payee_name": "test payee",
        "category_id": "cb7d3a9a-392c-4826-bbee-e6448591f475",
        "memo": "test memo",
        "cleared": "cleared",
        "approved": True,
        "flag_color": None,
        "subtransactions": [subtransaction_data],
    }
