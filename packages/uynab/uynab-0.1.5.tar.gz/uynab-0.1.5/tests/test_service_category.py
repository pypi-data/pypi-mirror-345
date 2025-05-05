from uuid import UUID

import pytest

from uynab.service.category import CategoryService


@pytest.fixture
def category_service(mock_client):
    return CategoryService(mock_client)


def test_get_all_categories(category_service, mock_client, category_group):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    category_group_1 = category_group
    category_group_1.id = UUID("87654321-4321-8765-4321-876543218765")
    category_group_2 = category_group
    category_group_2.id = UUID("12345678-1234-5678-1234-567812345678")

    mock_response = [category_group_1, category_group_2]
    mock_client.request.return_value = {
        "data": {
            "category_groups": mock_response,
            "server_knowledge": 1,
        }
    }

    categories = category_service.get_all_categories(budget_id)

    assert len(categories) == 2
    assert categories[0].id == category_group_1.id
    assert categories[0].categories[0].id == category_group_1.categories[0].id


def test_get_category(category_service, mock_client, category_data, category_id):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")

    mock_client.request.return_value = {"data": {"category": category_data}}

    category = category_service.get_category(budget_id, category_id)

    assert category.id == category_id


def test_get_all_categories_empty_groups(category_service, mock_client, category_group):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_client.request.return_value = {
        "data": {
            "category_groups": [
                {
                    "id": category_group.id,
                    "name": "Empty Group",
                    "hidden": False,
                    "deleted": False,
                    "categories": [],
                }
            ],
            "server_knowledge": 1,
        }
    }

    categories = category_service.get_all_categories(budget_id)
    assert categories[0].categories == []


def test_get_all_categories_group_with_no_categories(category_service, mock_client):
    budget_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_client.request.return_value = {
        "data": {
            "category_groups": [],
            "server_knowledge": 1,
        }
    }

    categories = category_service.get_all_categories(budget_id)
    assert categories == []
