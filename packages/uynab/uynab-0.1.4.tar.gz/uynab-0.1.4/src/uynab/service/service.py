"""
# Service module

This module provides the YNABService class, which handles communication with the YNAB API.

Classes:
    YNABService: A service class to handle communication with YNAB.
"""

from typing import Any, Callable, TypeVar

from pydantic import ValidationError

from uynab.abstract.client import Client
from uynab.error import ResponseError

Model = TypeVar("Model", bound=Callable)


class YNABService:
    """
    A service class to handle communication with YNAB.

    Attributes:
        client (Client): The client used for communication with YNAB.

    Methods:
        perform_api_call(model: Model, method: str, endpoint: str, data: dict | None = None) -> dict:
            Sends a request to the specified endpoint using the given method and data.
    """

    def __init__(self, client: Client) -> None:
        """Initialize service class

        Args:
            client (Client): client for communication with YNAB
        """
        self.client = client

    def perform_api_call(
        self,
        model: Model,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: Any | None = None,
    ) -> Model:
        """
        Perform an API call using the specified method and endpoint, and return the response as a model instance.

        Args:
            model (Model): The model class to instantiate with the response data.
            method (str): The HTTP method to use for the API call (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint to call.
            params (dict, optional): The query parameters to send with the API call. Defaults to None.
            data (Any, optional): The data to send with the API call. Defaults to None.

        Returns:
            Model: An instance of the model class populated with the response data.

        Raises:
            ResponseError: If the response data cannot be validated against the model.
        """

        response = self.client.request(method, endpoint, params=params, data=data)
        try:
            return model(**response)
        except ValidationError as e:
            raise ResponseError(response=response, verbose=self.client._verbose) from e
