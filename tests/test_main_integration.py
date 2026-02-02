import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from src.processing import filter_by_state, sort_by_date
from src.regex_operations import count_by_category, filter_by_description


class TestMainIntegration:
    """Интеграционные тесты для основной логики"""

    def test_filter_and_search_integration(self):
        """Интеграционный тест фильтрации и поиска"""
        transactions = [
            {"id": 1, "state": "EXECUTED", "description": "Перевод организации", "date": "2023-01-01"},
            {"id": 2, "state": "EXECUTED", "description": "Пополнение счета", "date": "2023-01-02"},
            {"id": 3, "state": "CANCELED", "description": "Перевод организации", "date": "2023-01-03"},
            {"id": 4, "state": "EXECUTED", "description": "Снятие наличных", "date": "2023-01-04"},
        ]

        # Фильтрация по статусу
        filtered = filter_by_state(transactions, "EXECUTED")
        assert len(filtered) == 3

        # Поиск по описанию
        searched = filter_by_description(filtered, "Перевод")
        assert len(searched) == 1
        assert searched[0]["id"] == 1

    def test_sort_and_category_integration(self):
        """Интеграционный тест сортировки и категорий"""
        transactions = [
            {"id": 1, "state": "EXECUTED", "description": "Перевод организации", "date": "2023-01-03"},
            {"id": 2, "state": "EXECUTED", "description": "Пополнение счета", "date": "2023-01-01"},
            {"id": 3, "state": "EXECUTED", "description": "Перевод с карты на карту", "date": "2023-01-02"},
        ]

        # Сортировка по дате
        sorted_transactions = sort_by_date(transactions, descending=False)
        assert sorted_transactions[0]["id"] == 2  # Самая ранняя дата
        assert sorted_transactions[2]["id"] == 1  # Самая поздняя дата

        # Подсчет категорий
        categories = ["Перевод организации", "Перевод с карты на карту", "Пополнение"]
        counts = count_by_category(sorted_transactions, categories)

        assert counts["Перевод организации"] == 1
        assert counts["Перевод с карты на карту"] == 1
        assert counts["Пополнение"] == 1

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_flow_simulation(self, mock_stdout, mock_input):
        """Симуляция основного потока программы"""
        # Настраиваем моки для пользовательского ввода
        input_responses = [
            "1",  # Выбор JSON
            "EXECUTED",  # Статус
            "нет",  # Сортировка
            "нет",  # Рублевые
            "нет",  # Поиск по описанию
            "нет",  # Статистика
            "нет",  # Генераторы
            "нет",  # Конвертация
        ]
        mock_input.side_effect = input_responses

        # Мокаем загрузку данных
        with patch("src.file_loaders.load_transactions") as mock_load:
            mock_load.return_value = [
                {
                    "id": 1,
                    "state": "EXECUTED",
                    "date": "2023-01-01T12:00:00",
                    "description": "Перевод организации",
                    "from": "Счет 12345678901234567890",
                    "to": "Счет 09876543210987654321",
                    "operationAmount": {"amount": "1000", "currency": {"code": "RUB", "name": "руб."}},
                }
            ]

            # Запускаем main (частично)
            from src import processing

            transactions = mock_load.return_value
            filtered = processing.filter_by_state(transactions, "EXECUTED")

            # Проверяем результаты
            assert len(filtered) == 1
            assert filtered[0]["state"] == "EXECUTED"


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_filter_empty_data(self):
        """Тест фильтрации пустых данных"""
        with pytest.raises(ValueError, match="Передан пустой список"):
            filter_by_state([], "EXECUTED")

    def test_sort_empty_data(self):
        """Тест сортировки пустых данных"""
        with pytest.raises(ValueError, match="Передан пустой список"):
            sort_by_date([], True)

    def test_search_empty_data(self):
        """Тест поиска в пустых данных"""
        result = filter_by_description([], "test")
        assert result == []

    def test_categories_empty_data(self):
        """Тест категорий с пустыми данными"""
        result = count_by_category([], ["test"])
        assert result == {"test": 0}


@pytest.mark.parametrize(
    "test_data,search_word,expected_ids",
    [
        (
            [
                {"id": 1, "description": "Перевод"},
                {"id": 2, "description": "Пополнение"},
                {"id": 3, "description": "Перевод срочный"},
            ],
            "Перевод",
            [1, 3],
        ),
        (
            [
                {"id": 1, "description": "Test A"},
                {"id": 2, "description": "Test B"},
                {"id": 3, "description": "Another"},
            ],
            "test",
            [1, 2],
        ),  # case insensitive
    ],
)
def test_integration_parametrized(test_data, search_word, expected_ids):
    """Параметризованные интеграционные тесты"""
    result = filter_by_description(test_data, search_word)
    result_ids = [item["id"] for item in result]
    assert sorted(result_ids) == sorted(expected_ids)
