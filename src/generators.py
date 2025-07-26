from typing import List, Union, Dict, Iterator, Iterable


def filter_by_currency(transactions: Iterable[Dict[str, object]], currency: str) -> Iterator[Dict[str, object]]:
    """Генератор, который фильтрует транзакции по заданной валюте."""
    for transaction in transactions:
        op_amount = transaction.get("operationAmount", {})
        if isinstance(op_amount, dict):
            curr = op_amount.get("currency", {})
            if isinstance(curr, dict) and curr.get("code") == currency:
                yield transaction


def transaction_descriptions(
    transactions: List[Dict[str, Union[int, str, Dict[str, str]]]],
) -> Iterator[Union[int, str, Dict[str, str]]]:
    """Генератор, который возвращает описание каждой транзакции по очереди."""
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """Генератор, который выдает номера банковских карт в формате XXXX XXXX XXXX XXXX."""
    for number in range(start, end + 1):
        card_number = "{:016d}".format(number)
        formatted_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"
        yield formatted_number
