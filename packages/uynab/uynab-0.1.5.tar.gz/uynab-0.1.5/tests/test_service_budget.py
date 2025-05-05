from uuid import UUID

import pytest

from uynab.service.budget import BudgetService, BudgetSettings


@pytest.fixture
def budget_service(mock_client):
    return BudgetService(mock_client)


@pytest.fixture
def mock_budget():
    return {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Test Budget",
        "last_modified_on": "2024-12-16T19:53:48.861Z",
        "first_month": "2024-12-16",
        "last_month": "2024-12-16",
        "date_format": {"format": "2024-12-16"},
        "currency_format": {
            "iso_code": "PLN",
            "example_format": "123 456,78",
            "decimal_digits": 2,
            "decimal_separator": ",",
            "symbol_first": False,
            "group_separator": " ",
            "currency_symbol": " z\u0142",
            "display_symbol": True,
        },
        "accounts": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "type": "checking",
                "on_budget": True,
                "closed": True,
                "note": "string",
                "balance": 0,
                "cleared_balance": 0,
                "uncleared_balance": 0,
                "transfer_payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "direct_import_linked": True,
                "direct_import_in_error": True,
                "last_reconciled_at": "2024-12-16T19:53:48.861Z",
                "debt_original_balance": 0,
                "debt_interest_rates": {
                    "2024-01-01": 0,
                    "2024-01-02": 0,
                    "2024-01-03": 0,
                },
                "debt_minimum_payments": {
                    "2024-01-04": 0,
                    "2024-01-05": 0,
                    "2024-01-06": 0,
                },
                "debt_escrow_amounts": {
                    "2024-01-07": 0,
                    "2024-01-08": 0,
                    "2024-01-09": 0,
                },
                "deleted": True,
            }
        ],
        "payees": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Test Payee",
                "transfer_account_id": None,
                "deleted": False,
            }
        ],
        "payee_locations": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "latitude": "string",
                "longitude": "string",
                "deleted": True,
            }
        ],
        "category_groups": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "hidden": True,
                "deleted": True,
                "categories": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "category_group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "category_group_name": "string",
                        "name": "string",
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
                        "goal_creation_month": "2024-12-16",
                        "goal_target": 0,
                        "goal_target_month": "2024-12-16",
                        "goal_percentage_complete": 0,
                        "goal_months_to_budget": 0,
                        "goal_under_funded": 0,
                        "goal_overall_funded": 0,
                        "goal_overall_left": 0,
                        "deleted": True,
                    }
                ],
            }
        ],
        "categories": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_group_name": "string",
                "name": "string",
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
                "goal_creation_month": "2024-12-16",
                "goal_target": 0,
                "goal_target_month": "2024-12-16",
                "goal_percentage_complete": 0,
                "goal_months_to_budget": 0,
                "goal_under_funded": 0,
                "goal_overall_funded": 0,
                "goal_overall_left": 0,
                "deleted": True,
            }
        ],
        "months": [
            {
                "month": "2024-12-16",
                "note": "string",
                "income": 0,
                "budgeted": 0,
                "activity": 0,
                "to_be_budgeted": 0,
                "age_of_money": 0,
                "deleted": True,
                "categories": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "category_group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "category_group_name": "string",
                        "name": "string",
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
                        "goal_creation_month": "2024-12-16",
                        "goal_target": 0,
                        "goal_target_month": "2024-12-16",
                        "goal_percentage_complete": 0,
                        "goal_months_to_budget": 0,
                        "goal_under_funded": 0,
                        "goal_overall_funded": 0,
                        "goal_overall_left": 0,
                        "deleted": True,
                    }
                ],
            }
        ],
        "transactions": [
            {
                "id": "string",
                "date": "2024-12-16",
                "amount": 0,
                "memo": "string",
                "cleared": "cleared",
                "approved": True,
                "flag_color": "red",
                "flag_name": "string",
                "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transfer_transaction_id": "string",
                "matched_transaction_id": "string",
                "import_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "import_payee_name": "string",
                "import_payee_name_original": "string",
                "debt_transaction_type": "payment",
                "deleted": True,
            }
        ],
        "subtransactions": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "amount": 0,
                "memo": "string",
                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payee_name": "string",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_name": "string",
                "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transfer_transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "deleted": True,
            }
        ],
        "scheduled_transactions": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "date_first": "2024-12-16",
                "date_next": "2024-12-16",
                "frequency": "never",
                "amount": 0,
                "memo": "string",
                "flag_color": "red",
                "flag_name": "string",
                "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "deleted": True,
            }
        ],
        "scheduled_subtransactions": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "scheduled_transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "amount": 0,
                "memo": "string",
                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "deleted": True,
            }
        ],
    }


@pytest.fixture
def budget_settings():
    return {
        "date_format": {"format": "YYYY-MM-DD"},
        "currency_format": {
            "iso_code": "PLN",
            "example_format": "123 456,78",
            "decimal_digits": 2,
            "decimal_separator": ",",
            "symbol_first": False,
            "group_separator": " ",
            "currency_symbol": " z\u0142",
            "display_symbol": True,
        },
    }


@pytest.fixture
def all_budgets(mock_budget):
    return [mock_budget]


def test_get_all_budgets(budget_service, mock_client, all_budgets, mock_budget):
    mock_response = {
        "data": {"budgets": all_budgets, "default_budget": mock_budget},
    }
    mock_client.request.return_value = mock_response
    budgets = budget_service.get_all_budgets()

    assert len(budgets) == 1
    assert budgets[0].id == UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    assert budgets[0].name == "Test Budget"


def test_get_budget(budget_service, mock_client, mock_budget):
    mock_client.request.return_value = {
        "data": {
            "budget": mock_budget,
            "server_knowledge": 0,
        }
    }

    budget = budget_service.get_budget("3fa85f64-5717-4562-b3fc-2c963f66afa6")

    assert budget.id == UUID(mock_budget["id"])
    assert budget.name == "Test Budget"


def test_get_budget_settings(budget_service, mock_client, mock_budget, budget_settings):
    mock_client.request.return_value = {
        "data": {
            "settings": budget_settings,
        }
    }

    settings = budget_service.get_budget_settings(mock_budget["id"])

    assert settings.currency_format == BudgetSettings(**budget_settings).currency_format


def test_get_budget_by_name(budget_service, mock_client, mock_budget):
    mock_client.request.return_value = {
        "data": {
            "budgets": [mock_budget],
            "default_budget": mock_budget,
        }
    }
    budget = budget_service._get_budget_by_name("Test Budget")

    assert budget.id == UUID(mock_budget["id"])
    assert budget.name == mock_budget["name"]


def test_get_budget_by_name_not_found(budget_service, mock_client, mock_budget):
    mock_client.request.return_value = {
        "data": {
            "budgets": [mock_budget],
            "default_budget": mock_budget,
        }
    }
    non_existing_budget = "None existing budget"

    with pytest.raises(ValueError) as err:
        budget_service._get_budget_by_name(non_existing_budget)

    assert str(err.value) == f"Budget '{non_existing_budget}' not found"


def test_get_budget_id(budget_service, mock_client, mock_budget):
    mock_client.request.return_value = {
        "data": {
            "budgets": [mock_budget],
            "default_budget": mock_budget,
        }
    }
    budget_id = budget_service._get_budget_id("Test Budget")

    assert budget_id == UUID(mock_budget["id"])


def test_get_budget_id_not_found(budget_service, mock_client, mock_budget):
    mock_client.request.return_value = {
        "data": {
            "budgets": [mock_budget],
            "default_budget": mock_budget,
        }
    }
    non_existing_budget = "None existing budget"

    with pytest.raises(ValueError) as err:
        budget_service._get_budget_id(non_existing_budget)

    assert str(err.value) == f"Budget '{non_existing_budget}' not found"
