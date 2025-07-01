from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(number_of_card_or_account: str) -> str:
    """Функция маскирует номер карты или счета"""
    if number_of_card_or_account[:4] == "Счет":
        return f"Счет {get_mask_account(int(number_of_card_or_account[5:]))}"
    else:
        return (
            f"{number_of_card_or_account[-17::-1][-1::-1]}{get_mask_card_number(int(number_of_card_or_account[-16:]))}"
        )


def get_date(date: str) -> str:
    """Функция преобразует дату в формат 'ДД.ММ.ГГГГ'"""
    return f"{date[8:10]}.{date[5:7]}.{date[:4]}"
