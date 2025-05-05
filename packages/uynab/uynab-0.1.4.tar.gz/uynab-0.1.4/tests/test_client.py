from unittest.mock import Mock, patch

import pytest
import requests

from uynab.client import APIClientException
from uynab.service.budget import BudgetService
from uynab.service.category import CategoryService
from uynab.service.payee import PayeeService
from uynab.service.transaction import TransactionService


def test_client_initialization(ynab_client):
    assert ynab_client.api_token == "test_token"
    assert ynab_client.base_url == "https://api.youneedabudget.com/v1"
    assert isinstance(ynab_client.session, requests.Session)
    assert ynab_client.session.headers["Authorization"] == "Bearer test_token"
    assert isinstance(ynab_client.budget, BudgetService)
    assert isinstance(ynab_client.category, CategoryService)
    assert isinstance(ynab_client.payee, PayeeService)
    assert isinstance(ynab_client.transaction, TransactionService)


@patch("uynab.client.requests.Session.request")
def test_client_request_success(mock_request, ynab_client):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"data": "test"}
    mock_request.return_value = mock_response

    response = ynab_client.request("GET", "test_endpoint")

    assert response == {"data": "test"}
    mock_request.assert_called_once_with(
        "GET",
        "https://api.youneedabudget.com/v1/test_endpoint",
        params=None,
        json=None,
        timeout=None,
    )


@patch("uynab.client.requests.Session.request")
def test_client_request_failure(mock_request, ynab_client):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.json.return_value = {
        "error": {"name": "TestError", "detail": "Test detail"}
    }
    mock_response.status_code = 404

    mock_request.return_value = mock_response

    with pytest.raises(APIClientException) as excinfo:
        ynab_client.request("GET", "test_endpoint")

    assert str(excinfo.value) == "Error 404: TestError - Test detail"
    mock_request.assert_called_once_with(
        "GET",
        "https://api.youneedabudget.com/v1/test_endpoint",
        params=None,
        json=None,
        timeout=None,
    )


@patch("uynab.client.requests.Session.request")
def test_client_request_failure_unknown_error(mock_request, ynab_client):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.json.return_value = {}
    mock_response.status_code = 500

    mock_request.return_value = mock_response

    with pytest.raises(APIClientException) as excinfo:
        ynab_client.request("GET", "test_endpoint")

    assert str(excinfo.value) == "Error 500: Unknown name - No details"
    mock_request.assert_called_once_with(
        "GET",
        "https://api.youneedabudget.com/v1/test_endpoint",
        params=None,
        json=None,
        timeout=None,
    )
