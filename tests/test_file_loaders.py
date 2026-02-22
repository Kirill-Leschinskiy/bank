import csv
import json
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.file_loaders import load_csv, load_json, load_transactions, load_xlsx


class TestLoadJson:
    """Тесты для функции load_json"""

    def test_load_valid_json(self):
        """Тест загрузки корректного JSON файла"""
        test_data = [{"id": 1, "name": "Test 1"}, {"id": 2, "name": "Test 2"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = load_json(temp_path)
            assert result == test_data
            assert len(result) == 2
        finally:
            os.unlink(temp_path)

    def test_load_json_not_list(self):
        """Тест загрузки JSON не являющегося списком"""
        test_data = {"id": 1, "name": "Test"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            with pytest.raises(TypeError, match="Данные в JSON файле должны быть списком"):
                load_json(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_json_file_not_found(self):
        """Тест загрузки несуществующего JSON файла"""
        with pytest.raises(FileNotFoundError):
            load_json("non_existent_file.json")

    def test_load_invalid_json(self):
        """Тест загрузки некорректного JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Некорректный JSON формат"):
                load_json(temp_path)
        finally:
            os.unlink(temp_path)


class TestLoadCsv:
    """Тесты для функции load_csv"""

    def test_load_valid_csv(self):
        """Тест загрузки корректного CSV файла"""
        csv_content = """id,description,amount,currency
1,Перевод организации,1000,RUB
2,Пополнение счета,500,RUB
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = load_csv(temp_path)
            assert len(result) == 2
            assert result[0]["id"] == "1"  # CSV читает как строку
            assert result[0]["description"] == "Перевод организации"
            assert result[0]["amount"] == 1000.0  # Преобразуется в float
            assert result[0]["currency"] == "RUB"
        finally:
            os.unlink(temp_path)

    def test_load_csv_with_operation_amount_json(self):
        """Тест загрузки CSV с JSON в поле operationAmount"""
        csv_content = """id,operationAmount
1,{"amount": "1000", "currency": {"code": "RUB", "name": "руб."}}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = load_csv(temp_path)
            assert len(result) == 1
            assert isinstance(result[0]["operationAmount"], dict)
            assert result[0]["operationAmount"]["amount"] == "1000"
            assert result[0]["operationAmount"]["currency"]["code"] == "RUB"
        finally:
            os.unlink(temp_path)

    def test_load_csv_empty_file(self):
        """Тест загрузки пустого CSV файла"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("")  # Пустой файл
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="CSV файл пуст или не содержит заголовков"):
                load_csv(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_csv_file_not_found(self):
        """Тест загрузки несуществующего CSV файла"""
        with pytest.raises(FileNotFoundError):
            load_csv("non_existent_file.csv")


class TestLoadXlsx:
    """Тесты для функции load_xlsx"""

    def test_load_xlsx_file_not_found(self):
        """Тест загрузки несуществующего XLSX файла"""
        with pytest.raises(FileNotFoundError):
            load_xlsx("non_existent_file.xlsx")

    def test_load_xlsx_import_error(self, monkeypatch):
        """Тест ошибки импорта openpyxl"""
        monkeypatch.setattr("src.file_loaders.openpyxl", None)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Для работы с XLSX файлами"):
                load_xlsx(temp_path)
        finally:
            os.unlink(temp_path)

    @patch("src.file_loaders.openpyxl")
    def test_load_xlsx_mocked(self, mock_openpyxl):
        """Тест загрузки XLSX с моком openpyxl"""
        # Мокаем workbook и sheet
        mock_workbook = MagicMock()
        mock_sheet = MagicMock()
        mock_openpyxl.load_workbook.return_value = mock_workbook
        mock_workbook.active = mock_sheet

        # Настраиваем mock для имитации данных
        mock_sheet[1] = [MagicMock(value="id"), MagicMock(value="description"), MagicMock(value="amount")]
        mock_sheet.iter_rows.return_value = [
            (1, "Перевод", 1000),
            (2, "Пополнение", 500),
        ]

        result = load_xlsx("test.xlsx")

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["description"] == "Перевод"
        assert result[0]["amount"] == 1000.0


class TestLoadTransactions:
    """Тесты для функции load_transactions"""

    @patch("src.file_loaders.load_json")
    def test_load_transactions_json(self, mock_load_json):
        """Тест загрузки JSON транзакций"""
        mock_load_json.return_value = [{"id": 1, "test": "data"}]

        result = load_transactions("json")

        mock_load_json.assert_called_once()
        assert "operations.json" in mock_load_json.call_args[0][0]
        assert result == [{"id": 1, "test": "data"}]

    @patch("src.file_loaders.load_csv")
    def test_load_transactions_csv(self, mock_load_csv):
        """Тест загрузки CSV транзакций"""
        mock_load_csv.return_value = [{"id": 1, "test": "data"}]

        result = load_transactions("csv")

        mock_load_csv.assert_called_once()
        assert "transactions.csv" in mock_load_csv.call_args[0][0]
        assert result == [{"id": 1, "test": "data"}]

    @patch("src.file_loaders.load_xlsx")
    def test_load_transactions_xlsx(self, mock_load_xlsx):
        """Тест загрузки XLSX транзакций"""
        mock_load_xlsx.return_value = [{"id": 1, "test": "data"}]

        result = load_transactions("xlsx")

        mock_load_xlsx.assert_called_once()
        assert "transaction_excel.xlsx" in mock_load_xlsx.call_args[0][0]
        assert result == [{"id": 1, "test": "data"}]

    def test_load_transactions_invalid_format(self):
        """Тест загрузки с неверным форматом файла"""
        with pytest.raises(ValueError, match="Неподдерживаемый формат файла"):
            load_transactions("invalid_format")

    def test_load_transactions_case_insensitive(self):
        """Тест загрузки с разным регистром"""
        with patch("src.file_loaders.load_json") as mock_load_json:
            mock_load_json.return_value = [{"id": 1}]

            # Проверяем разные варианты регистра
            for file_type in ["JSON", "Json", "jSoN", "json"]:
                load_transactions(file_type)
                mock_load_json.assert_called()
                mock_load_json.reset_mock()
