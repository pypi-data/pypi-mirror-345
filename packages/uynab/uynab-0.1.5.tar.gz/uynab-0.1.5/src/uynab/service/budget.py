"""
# Service budget module

This module provides the BudgetService class for interacting with budget-related endpoints of the YNAB API.

Classes:
    BudgetService: A service class for retrieving and managing budgets and their settings.
"""

from uuid import UUID

from uynab.model.budget import (
    Budget,
    BudgetSettings,
    BudgetSummary,
    ResponseBudget,
    ResponseBudgets,
    ResponseBudgetSettings,
)
from uynab.service.service import YNABService


class BudgetService(YNABService):
    def get_all_budgets(self) -> list[BudgetSummary]:
        """
        Retrieve all budgets from the API.
        This method performs an API call to fetch all budgets and returns them as a list of Budget objects.
        Returns:
            list[Budget]: A list of Budget objects retrieved from the API.
        """

        response = self.perform_api_call(ResponseBudgets, "GET", "budgets")
        return response.data.budgets

    def get_budget(self, budget_id: UUID) -> Budget:
        """
        Retrieve a budget by its ID.
        Args:
            budget_id (UUID): The ID of the budget to retrieve.
        Returns:
            Budget: The budget object corresponding to the provided ID.
        """

        response = self.perform_api_call(ResponseBudget, "GET", f"budgets/{budget_id}")
        return response.data.budget

    def get_budget_settings(self, budget_id: UUID) -> BudgetSettings:
        """
        Retrieve the settings for a specific budget.

        Args:
            budget_id (UUID): The ID of the budget for which to retrieve settings.

        Returns:
            BudgetSettings: The settings of the specified budget.
        """

        response = self.perform_api_call(
            ResponseBudgetSettings, "GET", f"budgets/{budget_id}/settings"
        )
        return response.data.settings

    # Not standard methods

    def _get_budget_by_name(self, budget_name: str) -> BudgetSummary:
        """
        Retrieve a budget by its name.
        Args:
            budget_name (str): The name of the budget to retrieve.
        Returns:
            Budget: The budget object with the specified name.
        Raises:
            ValueError: If the budget with the given name does not exist.
        """

        all_budgets = self.get_all_budgets()
        for budget in all_budgets:
            if budget.name == budget_name:
                return budget
        raise ValueError(f"Budget '{budget_name}' not found")

    def _get_budget_id(self, budget_name: str) -> UUID:
        """
        Retrieve the budget ID for a given budget name.
        Args:
            budget_name (str): The name of the budget.
        Returns:
            str: The ID of the budget.
        Raises:
            ValueError: If the budget with the given name does not exist.
        """

        budget = self._get_budget_by_name(budget_name)
        return budget.id
