def get_mask_card_number(card_number: str) -> str:
    """Функция маскирует номер карты в формате XXXX XX** **** XXXX, где X — это цифра номера"""
    if not isinstance(card_number, str):
        raise ValueError('Неправильный тип данных')
    if len(card_number) != 16:
        raise ValueError(f'Ожидалось 16, а получили {len(card_number)}')
    if not card_number.isdigit():
        raise ValueError('В номере карте должны быть только цифры')
    return f"{card_number[0:4]} {card_number[4:6]}** **** {card_number[12:]}"


def get_mask_account(account_number: str) -> str:
    """Функция маскирует номер счета в формате **XXXX, где X — это цифра номера"""
    if not isinstance(account_number, str):
        raise ValueError("Неправильный тип данных")
    if len(account_number) != 20:
        raise ValueError(f'Ожидалось 20, а получили {len(account_number)}')
    if not account_number.isdigit():
        raise ValueError('В номере счета должны быть только цифры')
    return f"**{account_number[-4:]}"
