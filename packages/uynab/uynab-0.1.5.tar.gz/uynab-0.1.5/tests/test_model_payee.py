from uuid import UUID

import pytest
from pydantic import ValidationError

from uynab.model.payee import Payee, RequestDataPayee, ResponsePayee, ResponsePayees


def test_payee_model():
    payee_data = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Test Payee",
        "transfer_account_id": None,
        "deleted": False,
    }
    payee = Payee(**payee_data)
    assert payee.id == UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    assert payee.name == "Test Payee"
    assert payee.transfer_account_id is None
    assert payee.deleted is False


def test_response_payee_model():
    response_data = {
        "data": {
            "payee": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Test Payee",
                "transfer_account_id": None,
                "deleted": False,
            }
        }
    }
    response_payee = ResponsePayee(**response_data)
    assert response_payee.data.payee.id == UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    assert response_payee.data.payee.name == "Test Payee"
    assert response_payee.data.payee.transfer_account_id is None
    assert response_payee.data.payee.deleted is False


def test_response_payees_model():
    response_data = {
        "data": {
            "payees": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "Test Payee 1",
                    "transfer_account_id": None,
                    "deleted": False,
                },
                {
                    "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "name": "Test Payee 2",
                    "transfer_account_id": None,
                    "deleted": False,
                },
            ],
            "server_knowledge": 123,
        }
    }
    response_payees = ResponsePayees(**response_data)
    assert len(response_payees.data.payees) == 2
    assert response_payees.data.payees[0].name == "Test Payee 1"
    assert response_payees.data.server_knowledge == 123


def test_request_payee_model():
    request_data = {"payee": {"name": "Updated Payee"}}
    request_payee = RequestDataPayee(**request_data)
    assert request_payee.payee.name == "Updated Payee"


def test_invalid_payee_model():
    invalid_data = {
        "id": "invalid-uuid",
        "name": "Test Payee",
        "transfer_account_id": None,
        "deleted": False,
    }
    with pytest.raises(ValidationError):
        Payee(**invalid_data)
