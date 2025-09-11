import logging
import os
import re
from typing import Dict, List

import pandas as pd

from config import DATA_DIR

csv_file_path = DATA_DIR / "transactions.csv"
excel_file_path = DATA_DIR / "transactions.xlsx"

logs_dir = DATA_DIR.parent / "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file_path = logs_dir / "transactions.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def read_transactions_from_csv(file_path: str) -> List[Dict]:
    logger.info(f"Попытка прочитать данные из CSV файла: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не найден.")
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    try:
        df = pd.read_csv(file_path)
        transactions = df.to_dict(orient="records")
        logger.info(f"Успешно считано {len(transactions)} транзакций из файла: {file_path}")
        return transactions
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        raise


def read_transactions_from_excel(file_path: str) -> List[Dict]:
    logger.info(f"Попытка прочитать данные из Excel файла: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не найден.")
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    try:
        df = pd.read_excel(file_path)
        transactions = df.to_dict(orient="records")
        logger.info(f"Успешно считано {len(transactions)} транзакций из файла: {file_path}")
        return transactions
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        raise


def filter_transactions(transactions: List[Dict], search_string: str) -> List[Dict]:
    logger.info(f"Попытка фильтрации транзакций по строке: {search_string}")
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)  # Компилируем шаблон
    filtered_transactions = [
        transaction for transaction in transactions if pattern.search(transaction.get("description", ""))
    ]
    logger.info(f"Найдено {len(filtered_transactions)} транзакций, соответствующих строке: {search_string}")
    return filtered_transactions


def count_transactions_by_category(transactions: List[Dict], categories: List[str]) -> Dict[str, int]:
    logger.info("Подсчет транзакций по категориям.")
    category_count = {category: 0 for category in categories}
    for transaction in transactions:
        description = transaction.get("description", "").lower()
        for category in categories:
            if category.lower() in description:
                category_count[category] += 1
    logger.info(f"Подсчет завершен. Результаты: {category_count}")
    return category_count
