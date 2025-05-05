"""
# Service payee module.

This module provides the `PayeeService` class, which encapsulates operations related to payees
in the YNAB API. It acts as an interface to manage payees for a given budget, including retrieving
payee details, fetching all payees, and updating payee information.

Classes:
    - PayeeService: A service for managing YNAB payees, providing methods to interact with the API.

Example Usage:
    ```py
    from uynab.client import YNABClient
    from uynab.service.payee import PayeeService

    # Initialize the API client
    client = YNABClient(api_token="your-token")

    # Initialize the PayeeService
    payee_service = PayeeService(client)

    # Fetch all payees for a specific budget
    budget_id = "some-budget-id"
    payees = payee_service.get_all_payees(budget_id)

    # Fetch details of a specific payee
    payee_id = "some-payee-id"
    payee = payee_service.get_payee(budget_id, payee_id)

    # Update a specific payee
    updated_payee = payee_service.update_payee(
        budget_id, payee_id, {"payee": {"name": "New Payee Name"}}
    )
    ```
"""

from uuid import UUID

from uynab.model.payee import Payee, RequestDataPayee, ResponsePayee, ResponsePayees
from uynab.service.service import YNABService


class PayeeService(YNABService):
    """
    A service for managing payees in the YNAB API.

    This class provides methods to interact with the payees associated with a specific budget,
    including fetching all payees, retrieving details for a single payee, and updating payee details.

    Attributes:
        client (Client): An instance of the YNAB API client used for making requests.

    Methods:
        get_all_payees(budget_id: UUID) -> list[Payee]:
            Fetch all payees associated with a specific budget.

        get_payee(budget_id: UUID, payee_id: UUID) -> Payee:
            Retrieve details for a single payee by ID.

        update_payee(budget_id: UUID, payee_id: UUID, data: dict) -> Payee:
            Update the details of a specific payee.
    """

    def get_all_payees(self, budget_id: UUID) -> list[Payee]:
        """Fetch all payees for the specific budget

        Args:
            budget_id (UUID): An ID for a budget from which all payees will be fetched

        Returns:
            list[Payee]: List of all payees for specified budget
        """
        response = self.perform_api_call(
            ResponsePayees, "GET", f"budgets/{budget_id}/payees"
        )
        return response.data.payees

    def get_payee(self, budget_id: UUID, payee_id: UUID) -> Payee:
        """Fetch a single payee

        Args:
            budget_id (UUID): An ID for the budget from which payee will be fetched
            payee_id (UUID): An ID of a payee to fetch

        Returns:
            Payee: Fetched payee
        """
        response = self.perform_api_call(
            ResponsePayee, "GET", f"budgets/{budget_id}/payees/{payee_id}"
        )
        return response.data.payee

    def update_payee(self, budget_id: UUID, payee_id: UUID, data: dict) -> Payee:
        """Update a single payee

        Args:
            budget_id (UUID): An ID for the budget from which payee will be updated
            payee_id (UUID): An ID of a payee to update
            data (dict): Data of payee to update in the following format:
                ```py
                {
                    "payee": {
                            "name": "string"
                        }
                }
                ```

        Returns:
            Payee: Updated payee
        """
        response = self.perform_api_call(
            ResponsePayee,
            "PATCH",
            f"budgets/{budget_id}/payees/{payee_id}",
            data=RequestDataPayee(**data).model_dump_json(),
        )
        return response.data.payee
