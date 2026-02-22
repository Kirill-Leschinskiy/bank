import json
import tempfile
import os
import pytest
from unittest.mock import patch, MagicMock
from src.utils import transactions_loaded, normalize_transaction_data


class TestTransactionsLoaded:
    """Тесты для функции transactions_loaded"""

    def test_load_transactions_with_real_file(self):
        """Тест загрузки с реальным временным файлом"""
        test_data = [
            {"id": 1, "amount": "100", "currency": "USD"},
            {"id": 2, "amount": "200", "currency": "RUB"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = transactions_loaded(temp_path)
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2
        finally:
            os.unlink(temp_path)

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_valid_file(self, mock_load_json, mock_logger):
        """Тест загрузки корректного JSON файла"""
        # Настраиваем мок
        mock_load_json.return_value = [{"id": 1, "amount": 100, "currency": "USD"}]

        result = transactions_loaded("data/operations.json")

        # Проверяем что функция load_json вызвана с правильным аргументом
        mock_load_json.assert_called_once_with("data/operations.json")

        # Проверяем результат
        assert result == [{"id": 1, "amount": 100, "currency": "USD"}]

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_not_list(self, mock_load_json, mock_logger):
        """Тест загрузки JSON, который не является списком"""
        # Настраиваем мок чтобы выбрасывал TypeError
        mock_load_json.side_effect = TypeError("Данные в JSON файле должны быть списком")

        result = transactions_loaded("data/operations.json")

        # Проверяем что возвращается пустой список
        assert result == []

        # Проверяем что логгер был вызван
        mock_logger.error.assert_called()

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_file_not_found(self, mock_load_json, mock_logger):
        """Тест загрузки несуществующего файла"""
        mock_load_json.side_effect = FileNotFoundError("Файл не найден")

        result = transactions_loaded("non_existent_file.json")
        assert result == []
        mock_logger.error.assert_called()

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_invalid_json(self, mock_load_json, mock_logger):
        """Тест загрузки некорректного JSON"""
        mock_load_json.side_effect = ValueError("Некорректный JSON формат")

        result = transactions_loaded("data/operations.json")
        assert result == []
        mock_logger.error.assert_called()

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_json_decode_error(self, mock_load_json, mock_logger):
        """Тест загрузки с ошибкой декодирования JSON"""
        mock_load_json.side_effect = json.JSONDecodeError("Expecting value", "test", 0)

        result = transactions_loaded("data/operations.json")
        assert result == []
        mock_logger.error.assert_called()

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_permission_error(self, mock_load_json, mock_logger):
        """Тест загрузки с ошибкой доступа"""
        mock_load_json.side_effect = PermissionError("Нет доступа к файлу")

        result = transactions_loaded("data/operations.json")
        assert result == []
        mock_logger.error.assert_called()

    @patch('src.utils.logger')
    @patch('src.file_loaders.load_json')
    def test_load_transactions_unexpected_error(self, mock_load_json, mock_logger):
        """Тест загрузки с непредвиденной ошибкой"""
        mock_load_json.side_effect = Exception("Неизвестная ошибка")

        result = transactions_loaded("data/operations.json")
        assert result == []
        mock_logger.error.assert_called()


class TestNormalizeTransactionData:
    """Тесты для функции normalize_transaction_data"""

    def test_normalize_complete_data(self):
        """Тест нормализации полных данных"""
        transactions = [
            {
                "id": 1,
                "state": "executed",
                "date": "2023-01-01",
                "description": "Test",
                "amount": "1000",
                "currency": "RUB",
                "from": "Счет 123",
                "to": "Счет 456"
            }
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 1
        assert result[0]["state"] == "EXECUTED"  # Приведено к верхнему регистру
        assert isinstance(result[0]["operationAmount"], dict)
        assert result[0]["operationAmount"]["amount"] == "1000"
        assert result[0]["operationAmount"]["currency"]["code"] == "RUB"
        assert result[0]["operationAmount"]["currency"]["name"] == "руб."

    def test_normalize_with_operation_amount(self):
        """Тест нормализации с уже существующим operationAmount"""
        transactions = [
            {
                "id": 1,
                "operationAmount": {
                    "amount": "500",
                    "currency": {"code": "USD", "name": "USD"}
                }
            }
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 1
        assert result[0]["operationAmount"]["amount"] == "500"
        assert result[0]["operationAmount"]["currency"]["code"] == "USD"

    def test_normalize_operation_amount_string(self):
        """Тест нормализации когда operationAmount - строка"""
        transactions = [
            {
                "id": 1,
                "operationAmount": '{"amount": "300", "currency": {"code": "EUR", "name": "Euro"}}'
            }
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 1
        assert isinstance(result[0]["operationAmount"], dict)
        assert result[0]["operationAmount"]["amount"] == "300"
        assert result[0]["operationAmount"]["currency"]["code"] == "EUR"

    def test_normalize_invalid_operation_amount_string(self):
        """Тест нормализации некорректного operationAmount строки"""
        transactions = [
            {
                "id": 1,
                "operationAmount": "invalid json"
            }
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 1
        assert isinstance(result[0]["operationAmount"], dict)
        assert result[0]["operationAmount"]["amount"] == "0"  # Значение по умолчанию

    def test_normalize_empty_transactions(self):
        """Тест нормализации пустого списка"""
        result = normalize_transaction_data([])
        assert result == []

    def test_normalize_invalid_transaction_type(self):
        """Тест нормализации с некорректным типом транзакции"""
        transactions = ["not a dict", 123, None]

        result = normalize_transaction_data(transactions)
        assert result == []  # Некорректные записи пропускаются

    def test_normalize_mixed_valid_invalid(self):
        """Тест нормализации смешанных валидных и невалидных данных"""
        transactions = [
            {"id": 1, "amount": "100", "currency": "RUB"},  # Valid
            "invalid",  # Invalid
            {"id": 2, "amount": "200", "currency": "USD"},  # Valid
            None,  # Invalid
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_normalize_state_variations(self):
        """Тест нормализации разных вариантов статуса"""
        transactions = [
            {"id": 1, "state": "executed"},
            {"id": 2, "state": "EXECUTED"},
            {"id": 3, "state": "Executed"},
            {"id": 4, "state": " canceled "},  # С пробелами
            {"id": 5, "state": ""},  # Пустая строка
            {"id": 6},  # Нет статуса
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 6  # Все транзакции должны быть обработаны
        assert result[0]["state"] == "EXECUTED"
        assert result[1]["state"] == "EXECUTED"
        assert result[2]["state"] == "EXECUTED"
        assert result[3]["state"] == "CANCELED"  # Пробелы убраны, приведено к верхнему регистру
        assert "state" not in result[4]  # Пустая строка - поле удалено
        assert "state" not in result[5]  # Нет статуса - поле не добавляется

    def test_normalize_currency_names(self):
        """Тест нормализации названий валют"""
        test_cases = [
            ("RUB", "руб."),
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
        ]

        for currency_code, expected_name in test_cases:
            transactions = [{"id": 1, "amount": "100", "currency": currency_code}]
            result = normalize_transaction_data(transactions)

            assert result[0]["operationAmount"]["currency"]["code"] == currency_code
            assert result[0]["operationAmount"]["currency"]["name"] == expected_name

    def test_normalize_with_special_characters(self):
        """Тест нормализации со специальными символами"""
        transactions = [
            {
                "id": 1,
                "description": "Перевод (срочный)",
                "amount": "1,000.50",  # С запятой и точкой
                "currency": "RUB"
            }
        ]

        result = normalize_transaction_data(transactions)

        assert len(result) == 1
        assert result[0]["operationAmount"]["amount"] == "1,000.50"  # Сохраняется как есть

    @pytest.mark.parametrize("input_state,expected_state", [
        ("executed", "EXECUTED"),
        ("EXECUTED", "EXECUTED"),
        ("canceled", "CANCELED"),
        ("CANCELED", "CANCELED"),
        ("pending", "PENDING"),
        ("PENDING", "PENDING"),
        ("", None),  # Пустая строка - поле удаляется
        (" ", None),  # Только пробел - поле удаляется
        ("ExEcUtEd", "EXECUTED"),  # Смешанный регистр
    ])
    def test_normalize_state_parametrized(self, input_state, expected_state):
        """Параметризованный тест нормализации статуса"""
        transactions = [{"id": 1, "state": input_state, "amount": "100", "currency": "RUB"}]

        result = normalize_transaction_data(transactions)

        if expected_state:
            assert result[0]["state"] == expected_state
        else:
            # Проверяем что поле state отсутствует
            assert "state" not in result[0]

    def test_normalize_removes_empty_state(self):
        """Тест что пустой state удаляется"""
        # Тест с разными пустыми значениями
        test_cases = [
            {"id": 1, "state": ""},
            {"id": 2, "state": " "},
            {"id": 3, "state": "  "},
            {"id": 4, "state": "\t"},
            {"id": 5, "state": "\n"},
            {"id": 6, "state": " \t\n "},
        ]

        result = normalize_transaction_data(test_cases)

        # Проверяем что все транзакции обработаны
        assert len(result) == 6

        # Проверяем что поле state отсутствует во всех
        for transaction in result:
            assert "state" not in transaction

    def test_normalize_preserves_valid_state(self):
        """Тест что валидный state сохраняется и нормализуется"""
        test_cases = [
            ({"id": 1, "state": "executed"}, "EXECUTED"),
            ({"id": 2, "state": "EXECUTED"}, "EXECUTED"),
            ({"id": 3, "state": " canceled "}, "CANCELED"),
            ({"id": 4, "state": "PENDING"}, "PENDING"),
        ]

        for input_transaction, expected_state in test_cases:
            transactions = [input_transaction]
            result = normalize_transaction_data(transactions)

            assert len(result) == 1
            assert result[0]["state"] == expected_state

    def test_normalize_copies_all_fields(self):
        """Тест что все поля копируются"""
        transaction = {
            "id": 1,
            "state": "executed",
            "date": "2023-01-01",
            "description": "Test",
            "amount": "1000",
            "currency": "RUB",
            "from": "Счет 123",
            "to": "Счет 456",
            "custom_field": "custom_value"  # Пользовательское поле
        }

        result = normalize_transaction_data([transaction])

        assert len(result) == 1
        # Проверяем что стандартные поля нормализованы
        assert result[0]["state"] == "EXECUTED"
        assert result[0]["operationAmount"]["amount"] == "1000"
        # Проверяем что пользовательское поле сохранено
        assert result[0]["custom_field"] == "custom_value"