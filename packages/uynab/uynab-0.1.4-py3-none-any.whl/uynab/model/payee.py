"""
# Model payee module.

This module contains Pydantic models for validating and managing data structures
related to payees in the YNAB API. These models ensure consistency when working
with API request and response payloads.

Classes:
    - Payee: Represents a single payee object.
    - ResponseDataPayee: Wraps a single payee in the response's `data` field.
    - ResponsePayee: Represents the full API response for a single payee.
    - ResponseDataPayees: Wraps a list of payees and server knowledge metadata.
    - ResponsePayees: Represents the full API response for multiple payees.
    - RequestPayee: Represents the structure of a single payee in request payloads.
    - RequestDataPayee: Wraps the `payee` field in request payloads.

Example Usage:
    ```py
    from uynab.model.payee import Payee, ResponsePayee

    # Validating a single payee response
    response_data = {
        "data": {
            "payee": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Test Payee",
                "transfer_account_id": None,
                "deleted": False
            }
        }
    }
    validated_response = ResponsePayee(**response_data)
    print(validated_response.data.payee.name)  # Output: Test Payee
    ```
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Payee(BaseModel):
    """
    Represents a payee in the YNAB system.

    Attributes:
        id (UUID): The unique identifier of the payee.
        name (str): The name of the payee.
        transfer_account_id (Optional[str]): The ID of the associated transfer account, if applicable.
        deleted (bool): Indicates whether the payee has been deleted.
    """

    id: UUID
    name: str
    transfer_account_id: Optional[UUID] = None
    deleted: bool


class ResponseDataPayee(BaseModel):
    """
    Represents the structure of the `data` field in a response containing a single payee.

    Attributes:
        payee (Payee): The payee object returned in the response.
    """

    payee: Payee


class ResponsePayee(BaseModel):
    """
    Represents the full API response containing a single payee.

    Attributes:
        data (ResponseDataPayee): The wrapper for the payee data in the response.
    """

    data: ResponseDataPayee


class ResponseDataPayees(BaseModel):
    """
    Represents the structure of the `data` field in a response containing multiple payees.

    Attributes:
        payees (list[Payee]): A list of payee objects.
        server_knowledge (int): A server-provided knowledge value for caching or synchronization.
    """

    payees: list[Payee]
    server_knowledge: int


class ResponsePayees(BaseModel):
    """
    Represents the full API response containing multiple payees.

    Attributes:
        data (ResponseDataPayees): The wrapper for the list of payee data and metadata in the response.
    """

    data: ResponseDataPayees


class RequestPayee(BaseModel):
    """
    Represents the structure of a request payload to update a payee.

    Attributes:
        name (str): The new name of the payee.
    """

    name: str


class RequestDataPayee(BaseModel):
    """
    Represents the structure of the `payee` field in a request payload.

    Attributes:
        payee (RequestPayee): The wrapper for the payee data in the request payload.
    """

    payee: RequestPayee
