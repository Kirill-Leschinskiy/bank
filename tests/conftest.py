import pytest


@pytest.fixture()
def invalid_data_int():
    return 12345


@pytest.fixture()
def invalid_data_list():
    return ['1234556790123276']


@pytest.fixture()
def invalid_data_empty_string():
    return ''


@pytest.fixture()
def invalid_data_few_digits():
    return '12345'


@pytest.fixture()
def invalid_data_many_digits():
    return '123455465354654765474777474'