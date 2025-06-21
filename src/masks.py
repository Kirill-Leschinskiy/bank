def get_mask_card_number(card_number: int) -> str:
    """Функция маскирует номер карты в формате XXXX XX** **** XXXX, где X — это цифра номера"""
    card_number_in_string = str(card_number)
    return f"{card_number_in_string[0:4]} {card_number_in_string[4:6]}** **** {card_number_in_string[12:]}"


def get_mask_account(account_number: int) -> str:
    """Функция маскирует номер счета в формате **XXXX, где X — это цифра номера"""
    account_number_in_string = str(account_number)
    return f"**{account_number_in_string[16:]}"
