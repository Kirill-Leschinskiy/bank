import json
import csv
import logging
import os
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("file_loaders")
logger.setLevel(logging.DEBUG)

if not os.path.exists("logs"):
    os.makedirs("logs")

file_handler = logging.FileHandler("logs/file_loaders.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.propagate = False


def load_json(file_path: str) -> List[Dict]:
    """Загружает данные из JSON файла"""
    path = Path(file_path)

    if not path.exists():
        logger.error(f"JSON файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, list):
                logger.warning("Данные в JSON файле не являются списком")
                raise TypeError("Данные в JSON файле должны быть списком")

            logger.info(f"Успешно загружено {len(data)} записей из JSON файла {path.name}")
            return data

    except json.JSONDecodeError as json_err:
        logger.error(f"Ошибка декодирования JSON: {json_err}")
        raise ValueError(f"Некорректный JSON формат в файле {path.name}")


def load_csv(file_path: str) -> List[Dict]:
    """Загружает данные из CSV файла"""
    path = Path(file_path)

    if not path.exists():
        logger.error(f"CSV файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            # Используем DictReader с явным указанием delimiter
            reader: csv.DictReader = csv.DictReader(file, delimiter=';')

            if not reader.fieldnames:
                raise ValueError("CSV файл пуст или не содержит заголовков")

            data: List[Dict[str, Any]] = []
            processed_count: int = 0

            for row_dict in reader:
                processed_count += 1

                # Создаем новый словарь с нормализованными ключами
                processed_row: Dict[str, Any] = {}

                # Явно аннотируем items() как список кортежей
                row_items: List[tuple[str, Any]] = list(row_dict.items())

                for key, value in row_items:
                    # Нормализуем ключи: убираем пробелы, приводим к нижнему регистру
                    normalized_key: str = key.strip().lower()

                    # Обрабатываем значения
                    if value is None or value == '':
                        processed_row[normalized_key] = None
                    else:
                        # Убираем лишние пробелы у строк
                        if isinstance(value, str):
                            processed_row[normalized_key] = value.strip()
                        else:
                            processed_row[normalized_key] = value

                if 'state' in processed_row and processed_row['state']:
                    state_value: Any = processed_row['state']
                    if isinstance(state_value, str):
                        processed_row['state'] = state_value.strip().upper()
                    else:
                        processed_row['state'] = str(state_value).strip().upper()

                if 'id' in processed_row and processed_row['id']:
                    try:
                        id_value: Any = processed_row['id']
                        if isinstance(id_value, str):
                            # Убираем возможные дробные части
                            id_str: str = id_value.split('.')[0]
                            processed_row['id'] = int(id_str)
                        else:
                            processed_row['id'] = int(id_value)
                    except (ValueError, TypeError):
                        pass

                data.append(processed_row)

                # Логируем прогресс для больших файлов
                if processed_count % 100 == 0:
                    logger.debug(f"Обработано {processed_count} записей из CSV")

            logger.info(f"Успешно загружено {len(data)} записей из CSV файла {path.name}")
            return data

    except csv.Error as csv_err:
        logger.error(f"Ошибка чтения CSV: {csv_err}")
        raise ValueError(f"Некорректный CSV формат в файле {path.name}")
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1251") as file:
                reader = csv.DictReader(file, delimiter=';')
                data = list(reader)
                logger.info(f"Загружено {len(data)} записей с кодировкой cp1251")
                return data
        except:
            raise ValueError(f"Некорректная кодировка файла {path.name}")


def load_xlsx(file_path: str) -> List[Dict]:
    """Загружает данные из XLSX файла"""
    try:
        import openpyxl
    except ImportError as import_err:
        logger.error("Библиотека openpyxl не установлена")
        raise ImportError(
            "Для работы с XLSX файлами установите openpyxl: pip install openpyxl"
        ) from import_err

    path = Path(file_path)

    if not path.exists():
        logger.error(f"XLSX файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        workbook = openpyxl.load_workbook(path, data_only=True)
        sheet = workbook.active

        # Получаем заголовки
        headers = []
        for cell in sheet[1]:
            if cell.value:
                headers.append(str(cell.value).strip())
            else:
                headers.append(f"column_{len(headers) + 1}")

        if not headers:
            raise ValueError("XLSX файл не содержит заголовков")

        # Читаем данные
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Пропускаем полностью пустые строки
            if all(cell is None for cell in row):
                continue

            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    # Обработка значений ячеек
                    if cell is None:
                        row_dict[headers[i]] = None
                    elif isinstance(cell, (int, float)):
                        row_dict[headers[i]] = cell
                    else:
                        row_dict[headers[i]] = str(cell).strip()

            # Автоматическое преобразование типов
            if 'id' in row_dict and row_dict['id'] is not None:
                try:
                    row_dict['id'] = int(row_dict['id'])
                except (ValueError, TypeError):
                    pass

            if 'amount' in row_dict and row_dict['amount'] is not None:
                try:
                    if isinstance(row_dict['amount'], str):
                        amount_str = row_dict['amount'].replace(',', '.')
                        row_dict['amount'] = float(amount_str)
                except (ValueError, TypeError):
                    pass

            data.append(row_dict)

        logger.info(f"Успешно загружено {len(data)} записей из XLSX файла {path.name}")
        return data

    except Exception as unexpected_err:
        logger.error(f"Ошибка при загрузке XLSX: {unexpected_err}")
        raise RuntimeError(f"Ошибка при загрузке XLSX файла {path.name}")


def load_transactions(file_type: str = "json") -> List[Dict]:
    """Загружает транзакции из файла указанного типа"""
    base_path = Path("data")

    if file_type.lower() == "json":
        file_path = base_path / "operations.json"
        return load_json(str(file_path))

    elif file_type.lower() == "csv":
        file_path = base_path / "transactions.csv"
        return load_csv(str(file_path))

    elif file_type.lower() == "xlsx":
        file_path = base_path / "transaction_excel.xlsx"
        return load_xlsx(str(file_path))

    else:
        error_msg = f"Неподдерживаемый формат файла: {file_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)