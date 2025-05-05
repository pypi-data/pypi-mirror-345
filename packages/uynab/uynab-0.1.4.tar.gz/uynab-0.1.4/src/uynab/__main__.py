import json
import unicodedata
from typing import Any, Sequence
from uuid import UUID

import click

from uynab.client import YNABClient
from uynab.model.account import Account
from uynab.model.budget import BudgetSummary
from uynab.model.category import CategoryGroup
from uynab.model.payee import Payee


def get_string_display_width(s: str) -> int:
    """
    Calculate the display width of a string, handling emoji and other Unicode characters.

    Args:
        s: Input string

    Returns:
        Display width of the string
    """
    width = 0
    for char in s:
        east_asian_width = unicodedata.east_asian_width(char)
        width += 2 if east_asian_width in ("F", "W") else 1
    return width


def format_table(
    data: Sequence[Sequence[str]], headers: Sequence[str] | None = None
) -> str:
    """
    Format a table from sequences of strings with optional headers, properly handling Unicode characters.

    Args:
        data: Sequence of sequences where each inner sequence represents a row
        headers: Optional sequence of column headers

    Returns:
        Formatted table as string with aligned columns
    """
    if not data:
        return ""

    # Add headers to data if provided
    all_rows = [headers] + list(data) if headers else list(data)

    # Calculate column widths using display width
    num_cols = len(all_rows[0])
    col_widths = [0] * num_cols
    for row in all_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], get_string_display_width(str(cell)))

    # Create the separator line
    separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"

    # Format each row
    def format_row(row: Sequence[str]) -> str:
        parts = []
        for cell, max_width in zip(row, col_widths):
            cell_str = str(cell)
            display_width = get_string_display_width(cell_str)
            padding = max_width - display_width
            parts.append(f" {cell_str}{' ' * padding} ")
        return "|" + "|".join(parts) + "|"

    # Build the table
    lines = [separator]

    if headers:
        lines.append(format_row(headers))
        lines.append(separator)

    # Add data rows
    for row in data:
        lines.append(format_row(row))

    lines.append(separator)

    return "\n".join(lines)


def parse_all_budget_list(budgets: list[BudgetSummary]) -> list[tuple]:
    """
    Convert a list of BudgetSummary objects into a list of tuples containing budget names and IDs.

    Args:
        budgets (list[BudgetSummary]): List of BudgetSummary objects to process

    Returns:
        list[tuple[str, UUID]]: List of tuples where each tuple contains (budget_name, budget_id)
    """
    return [(budget.name, budget.id) for budget in budgets]


def parse_all_category_list(categories: list[CategoryGroup]) -> list[tuple]:
    """
    Transforms a list of CategoryGroup objects into a list of tuples for display purposes.

    Each tuple in the resulting list contains either:
    - A category group header: ("--- Category Group ---", "--- {group_name} ---")
    - A category entry: (category_name, category_id)

    Args:
        categories (list[CategoryGroup]): List of CategoryGroup objects to be parsed

    Returns:
        list[tuple[str, UUID]]: List of tuples containing category group headers and category entries
    """
    result: list[tuple[Any, Any]] = []  # just for mypy to not throw errors
    for category_group in categories:
        result.append((f"{category_group.name}:", ""))
        for category in category_group.categories:
            result.append((f" - {category.name}", category.id))
    return result


def parse_all_account_list(accounts: list[Account]) -> list[tuple]:
    """
    Parse a list of Account objects into a list of tuples with basic account information.

    Args:
        accounts (list[Account]): A list of Account objects to be parsed.

    Returns:
        list[tuple[str, float, UUID]]: A list of tuples where each tuple contains:
            - account name (str)
            - account balance (float)
            - account ID (UUID)
    """
    return [(account.name, account.balance / 1000, account.id) for account in accounts]


def parse_all_payee_list(payees: list[Payee]) -> list[tuple]:
    return [(payee.name, payee.id, payee.transfer_account_id) for payee in payees]


def get_ynab_client() -> YNABClient:
    """Get a YNABClient instance, prompting for an API token if not already set."""
    client = YNABClient()

    if client.api_token is None:
        token = click.prompt("Please provide a token", type=str)
        client.set_token(token)

    return client


@click.group()
def cli():
    """YNAB CLI tool for managing budgets, accounts, and categories."""
    pass


@cli.group()
def budget():
    """Budget-related commands."""
    pass


@budget.command(name="list")
def list_budgets():
    """List all available budgets."""
    client = get_ynab_client()

    all_budgets = client.budget.get_all_budgets()
    to_print = parse_all_budget_list(all_budgets)
    result = format_table(to_print, ["Budget Name", "Budget ID"])

    click.echo(result)


@cli.group()
def account():
    """Account-related commands."""
    pass


@account.command(name="list")
@click.option(
    "--budget_id",
    required=True,
    type=UUID,
    help="ID of the budget to list accounts from",
)
def list_accounts(budget_id):
    """List accounts for a specific budget."""
    client = get_ynab_client()

    all_accounts = client.account.get_all_accounts(budget_id)
    to_print = parse_all_account_list(all_accounts)
    result = format_table(to_print, ["Account Name", "Account Balance", "Account ID"])

    click.echo(result)


@cli.group()
def category():
    """Category-related commands."""
    pass


@category.command(name="list")
@click.option(
    "--budget_id",
    required=True,
    type=UUID,
    help="ID of the budget to list categories from.",
)
def list_categories(budget_id):
    """List categories for a specific budget."""
    client = get_ynab_client()

    all_categories = client.category.get_all_categories(budget_id)
    to_print = parse_all_category_list(all_categories)
    result = format_table(to_print, ["Category Name", "Category ID"])

    click.echo(result)


@cli.group()
def payee():
    """Payees-related commands."""
    pass


@payee.command(name="list")
@click.option(
    "--budget_id", required=True, type=UUID, help="ID of a budget to list payees from."
)
@click.option(
    "--json",
    "json_output",
    required=False,
    is_flag=True,
    help="Print output in JSON format",
)
def list_payees(budget_id, json_output):
    """List payees for a specific budget."""
    client = get_ynab_client()

    all_payees = client.payee.get_all_payees(budget_id)

    if json_output:
        result = json.dumps([payee.model_dump(mode="json") for payee in all_payees])
    else:
        to_print = parse_all_payee_list(all_payees)
        result = format_table(to_print, ["Payee Name", "ID", "Transfer Account ID"])

    click.echo(result)


if __name__ == "__main__":
    cli()
