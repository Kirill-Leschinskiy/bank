import pytest


@pytest.fixture()
def invalid_data_int() -> int:
    return 12345


@pytest.fixture()
def invalid_data_list() -> list:
    return ["1234556790123276"]


@pytest.fixture()
def invalid_data_empty_string() -> str:
    return ""


@pytest.fixture()
def few_digits_for_card_number() -> str:
    return "12345"


@pytest.fixture()
def few_digits_for_account_number() -> str:
    return "12345342567819567"


@pytest.fixture()
def many_digits() -> str:
    return "12345546535465476547477747465"


@pytest.fixture()
def many_digits_for_widget_account() -> str:
    return "Счет 12345546535465476547477747465"


@pytest.fixture()
def many_digits_for_widget_card() -> str:
    return "Visa 12345546535465476547477747465"


@pytest.fixture()
def invalid_month() -> str:
    return "2025-00-22T18:35:29.512364"


@pytest.fixture()
def invalid_day() -> str:
    return "2023-01-35T18:35:29.512364"


@pytest.fixture()
def invalid_year() -> str:
    return "0031-01-35T18:35:29.512364"


@pytest.fixture()
def empty_data() -> list:
    return []
