import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "number_of_account_or_card, expected",
    [
        ("Счет 53647289102786491234", "Счет **1234"),
        ("Visa 5364728986491234", "Visa 5364 72** **** 1234"),
        ("MasterCard 1980728986491234", "MasterCard 1980 72** **** 1234"),
    ],
)
def test_mask_account_card(number_of_account_or_card: str, expected: str) -> None:
    assert mask_account_card(number_of_account_or_card) == expected


def test_raises_mask_account_card(
    invalid_data_empty_string: str, many_digits_for_widget_card: str, many_digits_for_widget_account: str
) -> None:
    with pytest.raises(ValueError):
        mask_account_card(invalid_data_empty_string)


@pytest.mark.parametrize(
    "date, expected_date",
    [
        ("2017-01-05T18:35:29.512364", "05.01.2017"),
        ("2019-05-10T18:35:29.512364", "10.05.2019"),
        ("2025-04-22T18:35:29.512364", "22.04.2025"),
    ],
)
def test_get_date(date: str, expected_date: str) -> None:
    assert get_date(date) == expected_date


def test_raises_get_date(
    invalid_data_empty_string: str, invalid_month: str, invalid_day: str, invalid_year: str
) -> None:
    with pytest.raises(ValueError):
        get_date(invalid_data_empty_string)
    with pytest.raises(ValueError):
        get_date(invalid_month)
    with pytest.raises(ValueError):
        get_date(invalid_day)
    with pytest.raises(ValueError):
        get_date(invalid_year)
