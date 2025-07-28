from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(number_of_card_or_account: str) -> str:
    """Функция маскирует номер карты или счета"""
    if number_of_card_or_account == "":
        raise ValueError("Неверный формат ввода")
    if number_of_card_or_account[:4] == "Счет":
        return f"Счет {get_mask_account(number_of_card_or_account[5:])}"
    else:
        return f"{number_of_card_or_account[-17::-1][-1::-1]}{get_mask_card_number(number_of_card_or_account[-16:])}"


def get_date(date: str) -> str:
    """Функция преобразует дату в формат 'ДД.ММ.ГГГГ'"""
    if len(date[:11]) != 11:
        raise ValueError("Неверный формат даты")
    if date[0] == "0" or date[5:7] == "00" or date[8:10] == "00" or date[5:7] > "12" or date[8:10] > "31":
        raise ValueError("Неверный формат даты")
    return f"{date[8:10]}.{date[5:7]}.{date[:4]}"
