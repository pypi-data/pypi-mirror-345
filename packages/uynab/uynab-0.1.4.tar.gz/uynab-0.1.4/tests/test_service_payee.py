import uuid

import pytest

from uynab.service.payee import PayeeService


@pytest.fixture
def payee_service(mock_client):
    return PayeeService(mock_client)


@pytest.fixture
def payee_id():
    return uuid.uuid4()


@pytest.fixture
def transfer_account_id():
    return uuid.uuid4()


def test_get_all_payees(payee_service, mock_client, budget_id):
    mock_response = {
        "data": {
            "payees": [
                {
                    "id": f"{uuid.uuid4()}",
                    "name": "Payee 1",
                    "transfer_account_id": None,
                    "deleted": False,
                },
                {
                    "id": f"{uuid.uuid4()}",
                    "name": "Payee 2",
                    "transfer_account_id": None,
                    "deleted": False,
                },
            ],
            "server_knowledge": 0,
        }
    }
    mock_client.request.return_value = mock_response
    payees = payee_service.get_all_payees(budget_id)
    assert len(payees) == 2
    assert payees[0].name == "Payee 1"
    assert payees[1].name == "Payee 2"


def test_get_payee(payee_service, mock_client, budget_id, payee_id):
    mock_response = {
        "data": {
            "payee": {
                "id": f"{payee_id}",
                "name": "Test Payee",
                "transfer_account_id": None,
                "deleted": False,
            }
        }
    }
    mock_client.request.return_value = mock_response
    payee = payee_service.get_payee(budget_id, payee_id)
    assert payee.id == payee_id
    assert payee.name == "Test Payee"


def test_update_payee(payee_service, mock_client, budget_id, payee_id):
    update_data = {"payee": {"name": "Updated Payee"}}
    mock_response = {
        "data": {
            "payee": {
                "id": f"{payee_id}",
                "name": "Updated Payee",
                "transfer_account_id": None,
                "deleted": False,
            }
        }
    }
    mock_client.request.return_value = mock_response
    updated_payee = payee_service.update_payee(budget_id, payee_id, update_data)
    assert updated_payee.name == "Updated Payee"
