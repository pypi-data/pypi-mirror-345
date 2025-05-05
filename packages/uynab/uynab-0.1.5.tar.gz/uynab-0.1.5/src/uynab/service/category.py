"""
# Service category module.

This module provides services for interacting with categories and category groups
within a budget in the YNAB (You Need A Budget) application.

Classes:
    CategoryService: A service class for retrieving category groups and categories
        from a specified budget.
"""

from uuid import UUID

from uynab.model.category import (
    Category,
    CategoryGroup,
    ResponseCategory,
    ResponseCategoryGroup,
)
from uynab.service.service import YNABService


class CategoryService(YNABService):
    def get_all_categories(self, budget_id: UUID) -> list[CategoryGroup]:
        """
        Retrieve all category groups for a given budget.
        Inside the category group there are categories.

        Args:
            budget_id (UUID): The unique identifier of the budget.

        Returns:
            list[CategoryGroup]: A list of category groups associated with the budget.
        """

        response = self.perform_api_call(
            ResponseCategoryGroup, "GET", f"budgets/{budget_id}/categories"
        )
        return response.data.category_groups

    def get_category(self, budget_id: UUID, category_id: UUID) -> Category:
        """
        Retrieve a specific category from a budget.

        Args:
            budget_id (UUID): The unique identifier of the budget.
            category_id (UUID): The unique identifier of the category.

        Returns:
            Category: The category object retrieved from the budget.
        """
        response = self.perform_api_call(
            ResponseCategory, "GET", f"budgets/{budget_id}/categories/{category_id}"
        )
        return response.data.category
