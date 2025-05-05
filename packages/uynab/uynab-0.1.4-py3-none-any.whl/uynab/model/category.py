"""
# Model category module.

This module defines models for representing financial categories and category groups within a budgeting application.

Classes:
    Category: Represents a financial category with various attributes such as id, name, budgeted amount, and goal details.
    ResponseDataCategory: Represents the response data for a single category.
    ResponseCategory: Represents the response structure for a category.
    CategoryGroup: Represents a group of categories with attributes such as id, name, and a list of categories.
    ResponseDataCategoryGroup: Represents the response data for a category group, including server knowledge.
    ResponseCategoryGroup: Represents the response structure for a category group.

Each class uses Pydantic's BaseModel to enforce type validation and provide serialization/deserialization capabilities.
"""

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class Category(BaseModel):
    """
    Category model representing a financial category.

    Attributes:
        id (UUID): Unique identifier for the category.
        category_group_id (UUID): Identifier for the category group.
        category_group_name (str): Name of the category group.
        name (str): Name of the category.
        hidden (bool): Indicates if the category is hidden.
        original_category_group_id (Optional[UUID]): Original identifier for the category group, if any.
        note (Optional[str]): Additional notes for the category.
        budgeted (int): Budgeted amount for the category.
        activity (int): Activity amount for the category.
        balance (int): Balance amount for the category.
        goal_type (Optional[Literal["TB", "TBD", "MF", "NEED", "DEBT"]]): Type of goal associated with the category.
        goal_needs_whole_amount (Optional[bool]): Indicates if the goal needs the whole amount.
        goal_day (Optional[int]): Day associated with the goal.
        goal_cadence (Optional[int]): Cadence of the goal.
        goal_cadence_frequency (Optional[int]): Frequency of the goal cadence.
        goal_creation_month (Optional[str]): Month when the goal was created.
        goal_target (Optional[int]): Target amount for the goal.
        goal_target_month (Optional[str]): Target month for the goal.
        goal_percentage_complete (Optional[int]): Percentage of goal completion.
        goal_months_to_budget (Optional[int]): Number of months to budget for the goal.
        goal_under_funded (Optional[int]): Amount underfunded for the goal.
        goal_overall_funded (Optional[int]): Overall funded amount for the goal.
        goal_overall_left (Optional[int]): Overall amount left for the goal.
        deleted (bool): Indicates if the category is deleted.
    """

    id: UUID
    category_group_id: UUID
    category_group_name: str
    name: str
    hidden: bool
    original_category_group_id: Optional[UUID] = None
    note: Optional[str] = None
    budgeted: int
    activity: int
    balance: int
    goal_type: Optional[Literal["TB", "TBD", "MF", "NEED", "DEBT"]] = None
    goal_needs_whole_amount: Optional[bool] = None
    goal_day: Optional[int] = None
    goal_cadence: Optional[int] = None
    goal_cadence_frequency: Optional[int] = None
    goal_creation_month: Optional[str] = None
    goal_target: Optional[int] = None
    goal_target_month: Optional[str] = None
    goal_percentage_complete: Optional[int] = None
    goal_months_to_budget: Optional[int] = None
    goal_under_funded: Optional[int] = None
    goal_overall_funded: Optional[int] = None
    goal_overall_left: Optional[int] = None
    deleted: bool


class ResponseDataCategory(BaseModel):
    """
    ResponseDataCategory is a model that represents the response data for a category.

    Attributes:
        category (Category): The category object associated with the response.
    """

    category: Category


class ResponseCategory(BaseModel):
    """
    ResponseCategory is a model representing the response structure for a category.

    Attributes:
        data (ResponseDataCategory): The data attribute containing the category details.
    """

    data: ResponseDataCategory


class CategoryGroup(BaseModel):
    """
    Represents a group of categories in the budgeting application.

    Attributes:
        id (UUID): The unique identifier of the category group.
        name (str): The name of the category group.
        hidden (bool): Indicates whether the category group is hidden.
        deleted (bool): Indicates whether the category group is deleted.
        categories (list[Category]): A list of categories that belong to this group.
    """

    id: UUID
    name: str
    hidden: bool
    deleted: bool
    categories: list[Category]


class ResponseDataCategoryGroup(BaseModel):
    """
    ResponseDataCategoryGroup represents the response data for a category group.

    Attributes:
        category_groups (list[CategoryGroup]): A list of category groups.
        server_knowledge (int): The server knowledge value.
    """

    category_groups: list[CategoryGroup]
    server_knowledge: int


class ResponseCategoryGroup(BaseModel):
    """
    ResponseCategoryGroup represents a category group in the response model.

    Attributes:
        data (ResponseDataCategoryGroup): The data associated with the category group.
    """

    data: ResponseDataCategoryGroup
