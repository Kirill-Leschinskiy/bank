import json
import logging
import os
from typing import Dict, List, Union

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/utils.log", mode="w")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)


def transactions_loaded(file_path: str) -> List[Dict[str, Union[int, str]]]:
    """Загружает транзакции из JSON-файла."""
    if not os.path.isfile(file_path):
        logger.error("Файла по такому пути не существует")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                logger.info(f"Транзакция успешно загружены из файла: {file_path}")
                return data
            else:
                logger.warning(f"Данные в файле {file_path} не являются списком")
                return []
        except json.JSONDecodeError as error:
            logger.error(f"Произошла ошибка при декодировании JSON из файла {file_path}: {error}")
            return []
