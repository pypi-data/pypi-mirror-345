import json

import pytest
from pydantic import ValidationError

from uynab.model.transaction import (
    NewTransaction,
    ResponseDataSaveTransactions,
    ResponseDataTransaction,
    ResponseDataTransactions,
    ResponseSaveTransactions,
    ResponseTransaction,
    ResponseTransactions,
    SaveSubTransaction,
    Subtransaction,
    TransactionDetail,
)


def test_subtransaction_creation(subtransaction_data, subtransaction_id):
    subtransaction = Subtransaction(**subtransaction_data)
    assert subtransaction.id == subtransaction_id
    assert subtransaction.amount == -16090
    assert subtransaction.memo == "test memo"


def test_subtransaction_invalid_uuid(subtransaction_data):
    subtransaction_data["id"] = "invalid-uuid"
    with pytest.raises(ValidationError):
        Subtransaction(**subtransaction_data)


def test_save_subtransaction_creation(savesubtransaction_data):
    save_subtransaction = SaveSubTransaction(**savesubtransaction_data)
    assert save_subtransaction.amount == -16090
    assert save_subtransaction.payee_name == "test payee"


def test_transaction_detail_creation(transaction_detail_data, transaction_detail_id):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    assert transaction_detail.id == transaction_detail_id
    assert transaction_detail.amount == -81080
    assert transaction_detail.cleared == "cleared"


def test_new_transaction_creation(new_transaction_data):
    new_transaction = NewTransaction(**new_transaction_data)
    assert new_transaction.amount == -81080
    assert new_transaction.cleared == "cleared"


def test_response_data_transaction(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_transaction = ResponseDataTransaction(transaction=transaction_detail)
    assert response_data_transaction.transaction.amount == -81080


def test_response_transaction(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_transaction = ResponseDataTransaction(transaction=transaction_detail)
    response_transaction = ResponseTransaction(data=response_data_transaction)
    assert response_transaction.data == response_data_transaction


def test_response_data_transactions(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_transactions = ResponseDataTransactions(
        transactions=[transaction_detail], server_knowledge=1
    )
    assert response_data_transactions.transactions[0] == transaction_detail
    assert response_data_transactions.server_knowledge == 1


def test_response_transactions(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_transactions = ResponseDataTransactions(
        transactions=[transaction_detail], server_knowledge=1
    )
    response_transactions = ResponseTransactions(data=response_data_transactions)
    assert response_transactions.data == response_data_transactions


def test_response_data_save_transactions(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_save_transactions = ResponseDataSaveTransactions(
        transaction_ids=[transaction_detail.id],
        transactions=[transaction_detail],
        duplicate_import_ids=[],
        server_knowledge=1,
    )
    assert response_data_save_transactions.transaction_ids == [transaction_detail.id]
    assert response_data_save_transactions.transactions[0] == transaction_detail
    assert response_data_save_transactions.duplicate_import_ids == []
    assert response_data_save_transactions.server_knowledge == 1


def test_response_save_transactions(transaction_detail_data):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    response_data_save_transactions = ResponseDataSaveTransactions(
        transaction_ids=[transaction_detail.id],
        transactions=[transaction_detail],
        duplicate_import_ids=[],
        server_knowledge=1,
    )
    response_save_transactions = ResponseSaveTransactions(
        data=response_data_save_transactions
    )
    assert response_save_transactions.data == response_data_save_transactions
    assert response_save_transactions.data.transaction_ids == [transaction_detail.id]
    assert response_save_transactions.data.transactions[0] == transaction_detail
    assert response_save_transactions.data.duplicate_import_ids == []
    assert response_save_transactions.data.server_knowledge == 1


def test_transaction_serialization(transaction_detail_data, transaction_detail_id):
    transaction_detail = TransactionDetail(**transaction_detail_data)
    transaction_json = json.loads(transaction_detail.model_dump_json())
    assert transaction_json["id"] == transaction_detail_id
    assert transaction_json["date"] == "2024-12-21"
    assert transaction_json["flag_color"] == "green"
