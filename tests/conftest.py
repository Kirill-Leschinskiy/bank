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


@pytest.fixture
def transactions():
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount":
            {
                "amount": "9824.07",
                "currency":
                    {
                        "name": "USD",
                        "code": "USD"
                    }
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount":
                {
                    "amount": "79114.93",
                    "currency":
                        {
                            "name": "USD",
                            "code": "USD"
                        }
                },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243004258542",
            "to": "Счет 75651667383060289041",
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount":
                {
                    "amount": "43318.34",
                    "currency":
                    {
                        "name": "руб.",
                        "code": "RUB"
                    }
                },
            "description": "Перевод организации",
            "from": "Счет 62094817784861134719",
            "to": "Счет 12574190247521191805",
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount":
                {
                    "amount": "56883.54",
                    "currency":
                    {
                        "name": "USD",
                        "code": "USD"
                    }
                },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount":
                {
                    "amount": "67314.70",
                    "currency":
                        {
                            "name": "руб.",
                            "code": "RUB"
                        }
                },
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14218585144415332012",
        },
    ]
