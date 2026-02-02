import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


@pytest.mark.parametrize(
    "start, end, expected",
    [
        (
            1,
            5,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
                "0000 0000 0000 0004",
                "0000 0000 0000 0005",
            ],
        ),
        (5, 5, ["0000 0000 0000 0005"]),
        (999999, 1000000, ["0000 0000 0099 9999", "0000 0000 0100 0000"]),
        (88, 91, ["0000 0000 0000 0088", "0000 0000 0000 0089", "0000 0000 0000 0090", "0000 0000 0000 0091"]),
    ],
)
def test_card_number_generator(start, end, expected):
    generated_numbers = list(card_number_generator(start, end))
    assert generated_numbers == expected
    assert list(card_number_generator(1, 0)) == []


def test_transaction_descriptions(transactions):
    descriptions = list(transaction_descriptions(transactions))
    expected_descriptions = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод организации",
        "Перевод с карты на карту",
        "Перевод организации",
    ]
    assert descriptions == expected_descriptions
    assert list(transaction_descriptions([])) == []


def test_filter_by_currency(transactions):
    usd_transactions = list(filter_by_currency(transactions, "USD"))
    assert {i["id"] for i in usd_transactions} == {939719570, 142264268, 895315941}

    rub_transactions = list(filter_by_currency(transactions, "RUB"))
    assert {i["id"] for i in rub_transactions} == {873106923, 594226727}

    assert list(filter_by_currency([], "USD")) == []

    no_currency_transactions = list(filter_by_currency(transactions, "BYN"))
    assert no_currency_transactions == []
