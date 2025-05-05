from abc import ABC, abstractmethod


class Client(ABC):
    """
    Abstract base class for a client that interacts with an API.

    Attributes:
        api_token (str or None): The API token used for authentication.
        base_url (str or None): The base URL for the API.

    Methods:
        request(method, endpoint, params, data):
            Abstract method to make a request to the API.
            Must be implemented by subclasses.
    """

    def __init__(
        self, api_token: None | str = None, base_url: None | str = None
    ) -> None:
        """
        Initialize the Client with an optional API token and base URL.

        Args:
            api_token (str or None): The API token used for authentication. Default is None.
            base_url (str or None): The base URL for the API. Default is None.
        """

        self.api_token = api_token
        self.base_url = base_url
        self._verbose = False

    @abstractmethod
    def request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: dict | None = None,
    ) -> dict:
        """
        Make a request to the API.

        Args:
            method (str): The HTTP method to use for the request (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint to send the request to.
            params (dict, optional): The query parameters to include in the request. Default is None.
            data (dict, optional): The data to include in the request body. Default is None.

        Returns:
            dict: The response from the API.
        """
