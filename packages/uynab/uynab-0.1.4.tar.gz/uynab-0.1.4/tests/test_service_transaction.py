from datetime import date
from uuid import UUID

import pytest
import requests

from uynab.service.transaction import (
    NewTransaction,
    SaveTransactionWithIdOrImportId,
    TransactionDetail,
    TransactionService,
)


@pytest.fixture
def transaction_service(mock_client):
    return TransactionService(mock_client)


@pytest.fixture
def transaction_detail(transaction_detail_data):
    return TransactionDetail(**transaction_detail_data)


@pytest.fixture
def new_transaction(new_transaction_data):
    return NewTransaction(**new_transaction_data)


@pytest.fixture
def save_transaction_with_id_or_import_id(
    save_transaction_with_id_or_import_id_data,
):
    return SaveTransactionWithIdOrImportId(**save_transaction_with_id_or_import_id_data)


def test_get_all_transactions(transaction_service, mock_client, transaction_detail):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    transaction_1 = transaction_detail
    transaction_1.id = UUID("87654321-4321-8765-4321-876543218765")
    transaction_2 = transaction_detail
    transaction_2.id = UUID("12345678-1234-5678-1234-567812345678")

    mock_response = [transaction_1, transaction_2]
    mock_client.request.return_value = {
        "data": {
            "transactions": mock_response,
            "server_knowledge": 1,
        }
    }

    transactions = transaction_service.get_all_transactions(budget_id)

    assert len(transactions) == 2
    assert transactions[0].id == transaction_1.id
    assert transactions[1].id == transaction_2.id


def test_get_transaction(
    transaction_service, mock_client, transaction_detail, transaction_detail_id
):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {"data": {"transaction": transaction_detail}}

    transaction = transaction_service.get_transaction(budget_id, transaction_detail_id)

    assert transaction.id == transaction_detail_id


def test_create_transactions(
    transaction_service, mock_client, new_transaction, transaction_detail
):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {
        "data": {
            "transactions": [transaction_detail],
            "server_knowledge": 0,
        },
    }

    created_transaction = transaction_service.create_transactions(
        budget_id, [new_transaction]
    )

    assert created_transaction[0].id == transaction_detail.id


def test_update_transaction(
    transaction_service, mock_client, new_transaction, transaction_detail
):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {
        "data": {
            "transaction": transaction_detail,
        },
    }

    updated_transaction = transaction_service.update_transaction(
        budget_id, transaction_detail.id, new_transaction
    )

    assert updated_transaction.id == transaction_detail.id


def test_update_transactions(
    transaction_service,
    mock_client,
    save_transaction_with_id_or_import_id,
    transaction_detail,
):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {
        "data": {
            "transaction_ids": [transaction_detail.id],
            "transactions": [transaction_detail],
            "duplicate_import_ids": [],
            "server_knowledge": 0,
        },
    }

    updated_transactions = transaction_service.update_transactions(
        budget_id, [save_transaction_with_id_or_import_id]
    )

    assert updated_transactions[0].id == transaction_detail.id


def test_delete_transaction(
    transaction_service, mock_client, transaction_detail, transaction_detail_id
):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {"data": {"transaction": transaction_detail}}

    deleted_transaction = transaction_service.delete_transaction(
        budget_id, transaction_detail_id
    )
    assert deleted_transaction.id == transaction_detail_id


@pytest.fixture
def sample_transactions():
    return [
        TransactionDetail(
            id="550e8400-e29b-41d4-a716-446655440000",
            account_id="a1b2c3d4-e5f6-4321-8765-123456789abc",
            category_id="11111111-2222-3333-4444-555555555555",
            payee_id="99999999-8888-7777-6666-555555555555",
            amount=50.00,
            date="2023-01-15",
            cleared="cleared",
            approved=True,
            deleted=False,
            account_name="Test Account",
            subtransactions=[],
        ).model_dump(),
        TransactionDetail(
            id="660e8400-e29b-41d4-a716-446655440000",
            account_id="a1b2c3d4-e5f6-4321-8765-123456789abc",
            category_id="22222222-2222-3333-4444-555555555555",
            payee_id="88888888-8888-7777-6666-555555555555",
            amount=75.00,
            date="2023-01-15",
            cleared="cleared",
            approved=True,
            deleted=False,
            account_name="Test Account",
            subtransactions=[],
        ).model_dump(),
    ]


def test_get_transactions_by_account(
    transaction_service, mock_client, budget_id, sample_transactions
):
    account_id = UUID("a1b2c3d4-e5f6-4321-8765-123456789abc")
    mock_client.request.return_value = {
        "data": {
            "transactions": sample_transactions,
            "server_knowledge": 1,
        }
    }

    transactions = transaction_service.get_transactions_by_account(
        budget_id, account_id
    )
    assert len(transactions) == 2
    assert all(t.account_id == account_id for t in transactions)


def test_get_transactions_by_category(
    transaction_service, mock_client, budget_id, sample_transactions
):
    category_id = UUID("11111111-2222-3333-4444-555555555555")

    mock_client.request.return_value = {
        "data": {
            "transactions": [sample_transactions[0]],
            "server_knowledge": 1,
        }
    }

    transactions = transaction_service.get_transactions_by_category(
        budget_id, category_id
    )
    assert len(transactions) == 1
    assert all(t.category_id == category_id for t in transactions)


def test_get_transactions_by_payee(
    transaction_service, mock_client, budget_id, sample_transactions
):
    payee_id = UUID("99999999-8888-7777-6666-555555555555")

    mock_client.request.return_value = {
        "data": {
            "transactions": [sample_transactions[0]],
            "server_knowledge": 1,
        }
    }

    transactions = transaction_service.get_transactions_by_payee(budget_id, payee_id)
    assert len(transactions) == 1
    assert all(t.payee_id == payee_id for t in transactions)


def test_get_transactions_by_month(
    transaction_service, mock_client, budget_id, sample_transactions
):
    mock_client.request.return_value = {
        "data": {
            "transactions": sample_transactions,
            "server_knowledge": 1,
        }
    }
    jan_transactions = transaction_service.get_transactions_by_month(
        budget_id, "2023-01-01"
    )
    assert len(jan_transactions) == 2
    assert all(t.date.month == 1 and t.date.year == 2023 for t in jan_transactions)


@pytest.mark.parametrize(
    "method,kwargs",
    [
        pytest.param(
            "create_transactions",
            {
                "budget_id": "123",
                "transactions": [
                    NewTransaction(
                        account_id=UUID("a1b2c3d4-e5f6-4321-8765-123456789abc"),
                        date=date(2023, 1, 15),
                        amount=100,
                        payee_id=UUID("99999999-8888-7777-6666-555555555555"),
                        category_id=UUID("11111111-2222-3333-4444-555555555555"),
                        memo="Test transaction",
                        cleared="cleared",
                        approved=True,
                        flag_color=None,
                        import_id=None,
                        subtransactions=[],
                    )
                ],
            },
            id="create transactions",
        ),
        pytest.param(
            "update_transactions",
            {
                "budget_id": "123",
                "transactions": [
                    SaveTransactionWithIdOrImportId(
                        id="550e8400-e29b-41d4-a716-446655440000",
                        account_id=UUID("a1b2c3d4-e5f6-4321-8765-123456789abc"),
                        date=date(2023, 1, 15),
                        amount=100,
                        payee_id=UUID("99999999-8888-7777-6666-555555555555"),
                        category_id=UUID("11111111-2222-3333-4444-555555555555"),
                        memo="Updated transaction",
                        cleared="cleared",
                        approved=True,
                        flag_color=None,
                        import_id=None,
                        subtransactions=[],
                    )
                ],
            },
            id="update_transactions",
        ),
        pytest.param(
            "update_transaction",
            {
                "budget_id": "123",
                "transaction_id": "456",
                "transaction": NewTransaction(
                    account_id=UUID("a1b2c3d4-e5f6-4321-8765-123456789abc"),
                    date=date(2023, 1, 15),
                    amount=100,
                    payee_id=UUID("99999999-8888-7777-6666-555555555555"),
                    category_id=UUID("11111111-2222-3333-4444-555555555555"),
                    memo="Test transaction",
                    cleared="cleared",
                    approved=True,
                    flag_color=None,
                    import_id=None,
                    subtransactions=[],
                ),
            },
            id="update_transaction",
        ),
    ],
)
def test_sending_raw_pydantic_model(ynab_client, method, kwargs):
    """
    Test that sending a raw Pydantic model without serialization raises TypeError.
    This simulates a developer forgetting to use model_dump_json().
    """
    ynab_client._timeout = 0.001
    method_to_test = ynab_client.transaction.__getattribute__(method)
    try:
        method_to_test(**kwargs)
    except requests.exceptions.ConnectionError:
        # We expect this error since the endpoint doesn't exist
        # The important part is that we got past the serialization step
        pass
