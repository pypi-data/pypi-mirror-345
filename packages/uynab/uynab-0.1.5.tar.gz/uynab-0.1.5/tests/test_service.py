from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from uynab.error import ResponseError
from uynab.service.service import YNABService


class Model(BaseModel):
    """Test Model"""

    success: bool


def test_service_request_success():
    client_mock = Mock()
    client_mock.request.return_value = {"success": True}
    service = YNABService(client=client_mock)

    response = service.perform_api_call(Model, "GET", "/test-endpoint")

    assert response.model_dump() == {"success": True}
    client_mock.request.assert_called_once_with(
        "GET", "/test-endpoint", params=None, data=None
    )


def test_service_request_validation_error():
    client_mock = Mock()
    client_mock.request.return_value = {"error": True}
    service = YNABService(client=client_mock)

    with pytest.raises(ResponseError) as e:
        service.perform_api_call(Model, "POST", "/test-endpoint", data={"key": "value"})

    assert str(e.value) == (
        "Cannot parse response from server. "
        "If you are sure that the response is correct, "
        "than please report this as a bug. "
        "Response: {'error': True}"
    )
    client_mock.request.assert_called_once_with(
        "POST", "/test-endpoint", params=None, data={"key": "value"}
    )
