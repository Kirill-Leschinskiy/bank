import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    "card_number, expected", [("1234567890123456", "1234 56** **** 3456"), ("7893567873803481", "7893 56** **** 3481")]
)
def test_get_mask_card_number(card_number: str, expected: str) -> None:
    assert get_mask_card_number(card_number) == expected


def test_raises_get_mask_card_number(
    invalid_data_int: int,
    invalid_data_list: list,
    invalid_data_empty_string: str,
    invalid_data_few_digits: str,
    many_digits: str,
) -> None:
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_int)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_list)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_empty_string)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_few_digits)
    with pytest.raises(ValueError):
        get_mask_card_number(many_digits)


@pytest.mark.parametrize(
    "account_number, expected", [("12345678901234564356", "**4356"), ("78935678738034823521", "**3521")]
)
def test_get_mask_account(account_number: str, expected: str) -> None:
    assert get_mask_account(account_number) == expected


def test_raises_get_mask_account(
    invalid_data_int: int,
    invalid_data_list: list,
    invalid_data_empty_string: str,
    few_digits_for_account_number: str,
    many_digits: str,
) -> None:
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_int)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_list)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_empty_string)
    with pytest.raises(ValueError):
        get_mask_card_number(few_digits_for_account_number)
    with pytest.raises(ValueError):
        get_mask_card_number(many_digits)
