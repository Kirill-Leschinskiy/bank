import json
import csv
import logging
import os
from typing import Dict, List

try:
    import openpyxl
except ImportError:
    openpyxl = None

logger = logging.getLogger("file_loaders")
logger.setLevel(logging.DEBUG)

if not os.path.exists("logs"):
    os.makedirs("logs")

file_handler = logging.FileHandler("logs/file_loaders.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def load_json(file_path: str) -> List[Dict]:
    """Загружает данные из JSON файла"""
    if not os.path.isfile(file_path):
        logger.error(f"JSON файл не найден: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                logger.info(f"Успешно загружено {len(data)} записей из JSON файла")
                return data
            else:
                logger.warning("Данные в JSON файле не являются списком")
                return []
    except Exception as e:
        logger.error(f"Ошибка при загрузке JSON: {e}")
        return []


def load_csv(file_path: str) -> List[Dict]:
    """Загружает данные из CSV файла"""
    if not os.path.isfile(file_path):
        logger.error(f"CSV файл не найден: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)

            # Преобразуем числовые значения
            for row in data:
                if "id" in row and row["id"].isdigit():
                    row["id"] = int(row["id"])
                if "amount" in row and row["amount"].replace(".", "", 1).isdigit():
                    row["amount"] = float(row["amount"])
                # Преобразуем вложенные структуры
                if "operationAmount" in row and row["operationAmount"]:
                    try:
                        row["operationAmount"] = json.loads(row["operationAmount"].replace("'", '"'))
                    except:
                        row["operationAmount"] = {
                            "amount": row.get("amount", ""),
                            "currency": {"code": "RUB", "name": "руб."},
                        }

            logger.info(f"Успешно загружено {len(data)} записей из CSV файла")
            return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке CSV: {e}")
        return []


def load_xlsx(file_path: str) -> List[Dict]:
    """Загружает данные из XLSX файла"""
    if openpyxl is None:
        logger.error("Библиотека openpyxl не установлена")
        print("Для работы с XLSX файлами установите openpyxl: pip install openpyxl")
        return []

    if not os.path.isfile(file_path):
        logger.error(f"XLSX файл не найден: {file_path}")
        return []

    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Получаем заголовки
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)

        # Читаем данные
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = cell

            # Преобразуем типы данных как в CSV
            if "id" in row_dict and isinstance(row_dict["id"], (int, float)):
                row_dict["id"] = int(row_dict["id"])
            if "amount" in row_dict and isinstance(row_dict["amount"], (int, float)):
                row_dict["amount"] = float(row_dict["amount"])

            data.append(row_dict)

        logger.info(f"Успешно загружено {len(data)} записей из XLSX файла")
        return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке XLSX: {e}")
        return []


def load_transactions(file_type: str = "json") -> List[Dict]:
    """Загружает транзакции из файла указанного типа"""
    base_path = "data"

    if file_type.lower() == "json":
        file_path = os.path.join(base_path, "operations.json")
        return load_json(file_path)

    elif file_type.lower() == "csv":
        file_path = os.path.join(base_path, "transactions.csv")
        return load_csv(file_path)

    elif file_type.lower() == "xlsx":
        file_path = os.path.join(base_path, "transaction_excel.xlsx")
        return load_xlsx(file_path)

    else:
        logger.error(f"Неподдерживаемый формат файла: {file_type}")
        return []
