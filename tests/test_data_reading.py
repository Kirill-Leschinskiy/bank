from unittest.mock import MagicMock, patch

import pytest

from src.data_reading import (count_transactions_by_category, filter_transactions, read_transactions_from_csv,
                              read_transactions_from_excel)


def test_read_transactions_from_csv():
    """Тестирование чтения транзакций из CSV файла."""
    mock_data = MagicMock()
    mock_data.to_dict.return_value = [{"amount": 100, "currency": "USD"}]

    with (
        patch("pandas.read_csv", return_value=mock_data),
        patch("os.path.exists", return_value=True),
    ):
        result = read_transactions_from_csv("mock_path.csv")
        assert result == [{"amount": 100, "currency": "USD"}]


def test_read_transactions_from_excel():
    """Тестирование чтения транзакций из Excel файла."""
    mock_data = MagicMock()
    mock_data.to_dict.return_value = [{"amount": 200, "currency": "EUR"}]

    with (
        patch("pandas.read_excel", return_value=mock_data),
        patch("os.path.exists", return_value=True),
    ):  # Подмена os.path.exists
        result = read_transactions_from_excel("mock_path.xlsx")
        assert result == [{"amount": 200, "currency": "EUR"}]


def test_file_not_found_csv():
    """Тестирование обработки ошибки при отсутствии CSV файла."""
    with patch("os.path.exists", return_value=False):  # Подмена os.path.exists
        with pytest.raises(FileNotFoundError):
            read_transactions_from_csv("non_existent_file.csv")


def test_file_not_found_excel():
    """Тестирование обработки ошибки при отсутствии Excel файла."""
    with patch("os.path.exists", return_value=False):  # Подмена os.path.exists
        with pytest.raises(FileNotFoundError):
            read_transactions_from_excel("non_existent_file.xlsx")


def test_filter_transactions():
    """Тестирование фильтрации транзакций по строке поиска."""
    transactions = [
        {"description": "Перевод с карты на карту", "amount": 1000, "currency": "RUB"},
        {"description": "Открытие вклада", "amount": 5000, "currency": "RUB"},
        {"description": "Перевод на счет", "amount": 2000, "currency": "USD"},
    ]
    search_string = "вклад"
    result = filter_transactions(transactions, search_string)
    assert len(result) == 1
    assert result[0]["description"] == "Открытие вклада"


def test_filter_transactions_no_match():
    """Тестирование фильтрации транзакций, когда нет совпадений."""
    transactions = [
        {"description": "Перевод с карты на карту", "amount": 1000, "currency": "RUB"},
        {"description": "Открытие вклада", "amount": 5000, "currency": "RUB"},
        {"description": "Перевод на счет", "amount": 2000, "currency": "USD"},
    ]
    search_string = "несуществующая операция"
    result = filter_transactions(transactions, search_string)
    assert len(result) == 0


def test_count_transactions_by_category():
    """Тестирование подсчета транзакций по категориям."""
    transactions = [
        {"description": "Перевод с карты на карту", "amount": 1000, "currency": "RUB"},
        {"description": "Открытие вклада", "amount": 5000, "currency": "RUB"},
        {"description": "Перевод на счет", "amount": 2000, "currency": "USD"},
    ]
    categories = ["перевод", "вклад"]
    result = count_transactions_by_category(transactions, categories)
    assert result["вклад"] == 1
    assert result["перевод"] == 2


def test_count_transactions_by_category_empty():
    """Тестирование подсчета транзакций по категориям, когда категории отсутствуют."""
    transactions = [
        {"description": "Перевод с карты на карту", "amount": 1000, "currency": "RUB"},
        {"description": "Открытие вклада", "amount": 5000, "currency": "RUB"},
    ]
    categories = ["неизвестная категория"]
    result = count_transactions_by_category(transactions, categories)
    assert result["неизвестная категория"] == 0
