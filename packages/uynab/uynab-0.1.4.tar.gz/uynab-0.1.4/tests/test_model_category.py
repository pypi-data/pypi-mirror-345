import pytest
from pydantic import ValidationError

from uynab.model.category import (
    Category,
    CategoryGroup,
    ResponseCategory,
    ResponseCategoryGroup,
    ResponseDataCategory,
    ResponseDataCategoryGroup,
)


def test_category_creation(category_data, category_id):
    category = Category(**category_data)
    assert category.id == category_id
    assert category.name == "Test Category"


def test_category_invalid_uuid(category_data):
    category_data["id"] = "invalid-uuid"
    with pytest.raises(ValidationError):
        Category(**category_data)


def test_response_data_category(category_data):
    category = Category(**category_data)
    response_data_category = ResponseDataCategory(category=category)
    assert response_data_category.category == category


def test_response_category(category_data):
    category = Category(**category_data)
    response_data_category = ResponseDataCategory(category=category)
    response_category = ResponseCategory(data=response_data_category)
    assert response_category.data == response_data_category


def test_category_group_creation(category_group_data, category_group_id):
    category_group = CategoryGroup(**category_group_data)
    assert category_group.id == category_group_id
    assert category_group.name == "Test Category Group"
    assert len(category_group.categories) == 1
    assert category_group.categories[0].name == "Test Category"


def test_response_data_category_group(category_group_data):
    category_group = CategoryGroup(**category_group_data)
    response_data_category_group = ResponseDataCategoryGroup(
        category_groups=[category_group], server_knowledge=1
    )
    assert response_data_category_group.category_groups[0] == category_group
    assert response_data_category_group.server_knowledge == 1


def test_response_category_group(category_group_data):
    category_group = CategoryGroup(**category_group_data)
    response_data_category_group = ResponseDataCategoryGroup(
        category_groups=[category_group], server_knowledge=1
    )
    response_category_group = ResponseCategoryGroup(data=response_data_category_group)
    assert response_category_group.data == response_data_category_group
