import json
import logging
import os
from typing import Dict, List

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/utils.log", mode="w")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)


def transactions_loaded(file_path: str) -> List[Dict]:
    """Загружает транзакции из JSON-файла (старая функция для совместимости)"""
    from src.file_loaders import load_json

    return load_json(file_path)


def normalize_transaction_data(transactions: List[Dict]) -> List[Dict]:
    """
    Нормализует структуру транзакций из разных источников
    к единому формату.
    """
    normalized = []

    for transaction in transactions:
        normalized_transaction = transaction.copy()

        # Нормализация поля state
        if "state" in normalized_transaction:
            normalized_transaction["state"] = str(normalized_transaction["state"]).upper()

        # Нормализация поля operationAmount для CSV/XLSX
        if "operationAmount" not in normalized_transaction or not normalized_transaction["operationAmount"]:
            amount = normalized_transaction.get("amount", "")
            currency_code = normalized_transaction.get("currency", "RUB")
            currency_name = "руб." if currency_code == "RUB" else currency_code

            normalized_transaction["operationAmount"] = {
                "amount": str(amount),
                "currency": {"code": str(currency_code), "name": str(currency_name)},
            }

        # Убедимся, что operationAmount - это словарь
        if isinstance(normalized_transaction.get("operationAmount"), str):
            try:
                normalized_transaction["operationAmount"] = json.loads(
                    normalized_transaction["operationAmount"].replace("'", '"')
                )
            except:
                normalized_transaction["operationAmount"] = {
                    "amount": "0",
                    "currency": {"code": "RUB", "name": "руб."},
                }

        normalized.append(normalized_transaction)

    return normalized
