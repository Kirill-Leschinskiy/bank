import pytest

from src.masks import get_mask_card_number

@pytest.mark.parametrize('card_number, expected',[('1234567890123456', '1234 56** **** 3456'),
                                                  ('7893567873803481', '7893 56** **** 3481')])
def test_get_mask_card_number(card_number, expected):
    assert get_mask_card_number(card_number) == expected


def test_raises_get_mask_card_number(invalid_data_int, invalid_data_list, invalid_data_empty_string, invalid_data_few_digits, invalid_data_many_digits):
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_int)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_list)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_empty_string)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_few_digits)
    with pytest.raises(ValueError):
        get_mask_card_number(invalid_data_many_digits)


def test_get_mask_account():
    pass
