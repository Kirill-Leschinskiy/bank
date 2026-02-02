import logging
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/masks.log", mode="w")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str:
    """Функция маскирует номер карты в формате XXXX XX** **** XXXX, где X — это цифра номера"""
    logger.debug(f"Получение маски для номера карты: {card_number}")
    if not isinstance(card_number, str):
        logger.error("Ошибка: Неправильный тип данных")
        raise ValueError("Неправильный тип данных")
    if len(card_number) != 16:
        logger.error(f"Ошибка: Ожидалось 16, а получили {len(card_number)}")
        raise ValueError(f"Ожидалось 16, а получили {len(card_number)}")
    if not card_number.isdigit():
        logger.error("Ошибка: В номере карты должны быть только цифры")
        raise ValueError("В номере карты должны быть только цифры")

    mask_card = f"{card_number[0:4]} {card_number[4:6]}** **** {card_number[12:]}"
    logger.info(f"Маска карты успешно создана: {mask_card}")

    return mask_card


def get_mask_account(account_number: str) -> str:
    """Функция маскирует номер счета в формате **XXXX, где X — это цифра номера"""
    logger.debug(f"Получение маски для номера счета: {account_number}")
    if not isinstance(account_number, str):
        logger.error("Ошибка: Неправильный тип данных")
        raise ValueError("Неправильный тип данных")
    if len(account_number) != 20:
        logger.error(f"Ошибка: Ожидалось 20, а получили {len(account_number)}")
        raise ValueError(f"Ожидалось 20, а получили {len(account_number)}")
    if not account_number.isdigit():
        logger.error("Ошибка: В номере счета должны быть только цифры")
        raise ValueError("В номере счета должны быть только цифры")

    mask_account = f"**{account_number[-4:]}"
    logger.info(f"Маска карты успешно создана: {mask_account}")

    return mask_account
