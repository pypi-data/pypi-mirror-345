## Installation

To install the package, use pip:

```sh
pip install uynab
```

## Instantiate Client

To communicate with YNAB API, you need to instantiate a client and YNAB API token.

Token can be passed as a parameter to `YNABClient`: `api_token="YOUR_YNAB_API_TOKEN"`

```python
from uynab.client import YNABClient

client = YNABClient(api_token="YOUR_YNAB_API_TOKEN")
```

Or you can use environmental variable `YNAB_API_TOKEN`:

```sh
export YNAB_API_TOKEN='YOUR_YNAB_API_TOKEN'
```

```python
from uynab.client import YNABClient

client = YNABClient()
```

## Get all budgets

Get all the information about all the budgets in your account.

```python
all_budgets = client.budget.get_all_budgets()
print(all_budgets)
```

## Find budget ID

Budget ID is used almost for every request in YNAB API. So it is very useful
to find it once and reuse it.

Here is how it can be easily done:

```python
budget_name = "Example Budget"
budget_id = None

all_budgets = client.budget.get_all_budgets()

for budget in all_budgets:
    if budget.name == budget_name:
        budget_id = budget.id

print(budget_id)
```

## Get all the payees

```python
payee_service = PayeeService(client=client)
payees = payee_service.get_all_payees(budget_id=budget_id)
```

## Get all categories

```python
category_service = CategoryService(client=client)
categories = category_service.get_all_categories(budget_id=budget_id)
```

## Get all transactions

```python
transaction_service = TransactionService(client=client)
transactions = transaction_service.get_all_transactions(budget_id=budget_id)
```