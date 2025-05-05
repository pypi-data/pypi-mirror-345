import pytest

from uynab.model.budget import (
    Budget,
    BudgetSettings,
    ResponseBudget,
    ResponseBudgetSettings,
    ResponseDataBudget,
    ResponseDataBudgetSettings,
)


@pytest.fixture
def budget_data(budget_id):
    return {
        "id": budget_id,
        "name": "Test Budget",
        "last_modified_on": "2023-10-01",
        "first_month": "2023-01-01",
        "last_month": "2023-10-01",
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
        "accounts": [],
        "payees": [],
        "payee_locations": [],
        "category_groups": [],
        "categories": [],
        "months": [],
        "transactions": [],
        "subtransactions": [],
        "scheduled_transactions": [],
        "scheduled_subtransactions": [],
        "server_knowledge": 0,
    }


def test_budget_creation(budget_data, budget_id):
    budget = Budget(**budget_data)
    assert budget.id == budget_id
    assert budget.name == "Test Budget"


def test_response_data_budget_creation(budget_data, budget_id):
    budget = Budget(**budget_data)
    response_data_budget = ResponseDataBudget(budget=budget, server_knowledge=0)
    assert response_data_budget.budget.id == budget_id
    assert response_data_budget.server_knowledge == 0


def test_response_budget_creation(budget_data, budget_id):
    budget = Budget(**budget_data)
    response_data_budget = ResponseDataBudget(budget=budget, server_knowledge=0)
    response_budget = ResponseBudget(data=response_data_budget)
    assert response_budget.data.budget.id == budget_id


def test_budget_settings_creation():
    settings_data = {
        "date_format": {"format": "MM/DD/YYYY"},
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
    budget_settings = BudgetSettings(**settings_data)
    assert budget_settings.date_format.format == "MM/DD/YYYY"
    assert budget_settings.currency_format.iso_code == "PLN"


def test_response_budget_settings_creation():
    settings_data = {
        "date_format": {"format": "MM/DD/YYYY"},
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
    budget_settings = BudgetSettings(**settings_data)
    response_data_budget_settings = ResponseDataBudgetSettings(settings=budget_settings)
    response_budget_settings = ResponseBudgetSettings(
        data=response_data_budget_settings
    )
    assert response_budget_settings.data.settings.date_format.format == "MM/DD/YYYY"
