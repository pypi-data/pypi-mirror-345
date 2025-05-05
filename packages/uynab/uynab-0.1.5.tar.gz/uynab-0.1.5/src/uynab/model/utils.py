from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from uynab.model.category import Category


class DateFormat(BaseModel):
    """A class used to represent a Date Format.

    Attributes:
        format (str): A string representing the date format.
            For example: "YYYY-MM-DD"
    """

    format: str


class CurrencyFormat(BaseModel):
    """
    CurrencyFormat is a model that represents the formatting details for a specific currency.

    Attributes:
        iso_code (str): The ISO 4217 code for the currency (e.g., 'USD' for US Dollar).
        example_format (str): An example of how the currency is formatted (e.g., '$1,234.56').
        decimal_digits (int): The number of decimal digits used in the currency (e.g., 2 for USD).
        decimal_separator (str): The character used to separate the integer part from the fractional part (e.g., '.' for USD).
        symbol_first (bool): Indicates whether the currency symbol appears before the amount (True) or after (False).
        group_separator (str): The character used to separate groups of thousands (e.g., ',' for USD).
        currency_symbol (str): The symbol used to represent the currency (e.g., '$' for USD).
        display_symbol (bool): Indicates whether the currency symbol should be displayed (True) or not (False).
    """

    iso_code: str
    example_format: str
    decimal_digits: int
    decimal_separator: str
    symbol_first: bool
    group_separator: str
    currency_symbol: str
    display_symbol: bool


class Month(BaseModel):
    """
    Represents a financial month with various attributes.

    Attributes:
        month (datetime): The month this instance represents.
        note (Optional[str]): An optional note for the month.
        income (int): The total income for the month.
        budgeted (int): The total amount budgeted for the month.
        activity (int): The total financial activity for the month.
        to_be_budgeted (int): The amount left to be budgeted for the month.
        age_of_money (int): The age of money in days.
        deleted (bool): Indicates if the month record is deleted.
        categories (list[Category]): A list of categories associated with the month.
    """

    month: datetime
    note: Optional[str] = None
    income: int
    budgeted: int
    activity: int
    to_be_budgeted: int
    age_of_money: int
    deleted: bool
    categories: list[Category]


class FlagColor(StrEnum):
    """A class used to represent the color of a flag.

    Attributes:
        RED: A red flag.
        ORANGE: An orange flag.
        YELLOW: A yellow flag.
        GREEN: A green flag.
        BLUE: A blue flag.
        PURPLE: A purple flag.
    """

    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
