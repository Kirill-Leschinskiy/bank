import json
import logging
import os
from typing import Dict, List

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.propagate = False  # Отключаем распространение логов


def transactions_loaded(file_path: str) -> List[Dict]:
    """Загружает транзакции из JSON-файла"""
    try:
        from src.file_loaders import load_json
        return load_json(file_path)
    except (FileNotFoundError, ValueError, TypeError, PermissionError, json.JSONDecodeError) as e:
        # Логируем ошибку, но не падаем
        logger.error(f"Ошибка при загрузке транзакций из {file_path}: {type(e).__name__} - {e}")
        return []
    except ImportError as e:
        logger.error(f"Не удалось импортировать file_loaders: {e}")
        raise  # Пробрасываем ошибку импорта дальше
    except Exception as e:
        # Ловим любые другие исключения
        logger.error(f"Неизвестная ошибка при загрузке транзакций: {type(e).__name__} - {e}")
        return []


def normalize_transaction_data(transactions: List[Dict]) -> List[Dict]:
    """
    Нормализует структуру транзакций из разных источников
    к единому формату.
    """
    if not isinstance(transactions, list):
        raise TypeError("transactions должен быть списком")

    normalized = []

    for i, transaction in enumerate(transactions):
        if not isinstance(transaction, dict):
            logger.warning(f"Транзакция {i} не является словарем, пропускаем")
            continue

        try:
            normalized_transaction = transaction.copy()

            # Нормализация поля state - удаляем пустые значения
            if "state" in normalized_transaction:
                state = str(normalized_transaction["state"]).strip()
                if state:  # Только если строка не пустая после удаления пробелов
                    normalized_transaction["state"] = state.upper()
                else:
                    # Удаляем поле если оно пустое или содержит только пробелы
                    del normalized_transaction["state"]

            # Нормализация поля operationAmount
            if "operationAmount" not in normalized_transaction or not normalized_transaction["operationAmount"]:
                amount = normalized_transaction.get("amount", "0")
                currency_code = normalized_transaction.get("currency", "RUB")
                currency_name = "руб." if str(currency_code).upper() == "RUB" else str(currency_code)

                normalized_transaction["operationAmount"] = {
                    "amount": str(amount),
                    "currency": {
                        "code": str(currency_code),
                        "name": currency_name
                    }
                }

            # Убедимся, что operationAmount - это словарь
            op_amount = normalized_transaction.get("operationAmount")
            if isinstance(op_amount, str):
                try:
                    # Пытаемся распарсить как JSON
                    normalized_transaction["operationAmount"] = json.loads(
                        op_amount.replace("'", '"')
                    )
                except json.JSONDecodeError:
                    # Если не JSON, создаем простую структуру
                    normalized_transaction["operationAmount"] = {
                        "amount": "0",
                        "currency": {"code": "RUB", "name": "руб."}
                    }

            normalized.append(normalized_transaction)

        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Ошибка при нормализации транзакции {i}: {e}")
            continue

    logger.info(f"Успешно нормализовано {len(normalized)} из {len(transactions)} транзакций")
    return normalized