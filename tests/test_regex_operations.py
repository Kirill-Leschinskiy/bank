import pytest

from src.regex_operations import count_by_category, filter_by_description

# Тестовые данные
SAMPLE_TRANSACTIONS = [
    {"id": 1, "description": "Перевод организации", "amount": 100},
    {"id": 2, "description": "Перевод с карты на карту", "amount": 200},
    {"id": 3, "description": "Открытие вклада", "amount": 300},
    {"id": 4, "description": "Перевод организации", "amount": 400},
    {"id": 5, "description": "Пополнение счета", "amount": 500},
    {"id": 6, "description": "Снятие наличных", "amount": 600},
    {"id": 7, "description": "Перевод со счета на счет", "amount": 700},
]


class TestFilterByDescription:
    """Тесты для функции filter_by_description"""

    def test_filter_existing_word(self):
        """Тест фильтрации по существующему слову"""
        result = filter_by_description(SAMPLE_TRANSACTIONS, "организации")
        assert len(result) == 2
        assert all("организации" in t["description"].lower() for t in result)
        assert result[0]["id"] == 1
        assert result[1]["id"] == 4

    def test_filter_case_insensitive(self):
        """Тест фильтрации без учета регистра"""
        result = filter_by_description(SAMPLE_TRANSACTIONS, "ПЕРЕВОД")
        assert len(result) == 4  # Все переводы

    def test_filter_non_existing_word(self):
        """Тест фильтрации по несуществующему слову"""
        result = filter_by_description(SAMPLE_TRANSACTIONS, "несуществующее")
        assert len(result) == 0

    def test_filter_empty_string(self):
        """Тест фильтрации по пустой строке"""
        result = filter_by_description(SAMPLE_TRANSACTIONS, "")
        assert len(result) == 0

    def test_filter_partial_word(self):
        """Тест фильтрации по части слова"""
        result = filter_by_description(SAMPLE_TRANSACTIONS, "вклад")
        assert len(result) == 1
        assert result[0]["description"] == "Открытие вклада"

    def test_filter_empty_list(self):
        """Тест фильтрации пустого списка"""
        result = filter_by_description([], "перевод")
        assert result == []

    def test_filter_special_characters(self):
        """Тест фильтрации со специальными символами"""
        transactions = [
            {"id": 1, "description": "Пополнение (срочное)", "amount": 100},
            {"id": 2, "description": "Снятие-наличных", "amount": 200},
        ]
        result = filter_by_description(transactions, "срочное")
        assert len(result) == 1
        assert result[0]["description"] == "Пополнение (срочное)"


class TestCountByCategory:
    """Тесты для функции count_by_category"""

    def test_count_categories(self):
        """Тест подсчета по категориям"""
        categories = ["Перевод организации", "Открытие вклада", "Пополнение"]
        result = count_by_category(SAMPLE_TRANSACTIONS, categories)

        assert result["Перевод организации"] == 2
        assert result["Открытие вклада"] == 1
        assert result["Пополнение"] == 1  # "Пополнение" не равно "Пополнение счета"

    def test_count_case_insensitive(self):
        """Тест подсчета без учета регистра"""
        categories = ["перевод организации", "ОТКРЫТИЕ ВКЛАДА"]
        result = count_by_category(SAMPLE_TRANSACTIONS, categories)

        assert result["перевод организации"] == 2
        assert result["ОТКРЫТИЕ ВКЛАДА"] == 1

    def test_count_empty_categories(self):
        """Тест подсчета с пустым списком категорий"""
        result = count_by_category(SAMPLE_TRANSACTIONS, [])
        assert result == {}

    def test_count_empty_transactions(self):
        """Тест подсчета с пустым списком транзакций"""
        result = count_by_category([], ["Перевод"])
        assert result["Перевод"] == 0

    def test_count_partial_match(self):
        """Тест подсчета с частичным совпадением"""
        categories = ["Перевод", "счет"]
        result = count_by_category(SAMPLE_TRANSACTIONS, categories)

        assert result["Перевод"] == 4  # Все переводы
        assert result["счет"] == 2  # "Пополнение счета" и "Перевод со счета на счет"

    def test_count_mixed_categories(self):
        """Тест подсчета смешанных категорий"""
        transactions = [
            {"id": 1, "description": "Перевод организации Сбербанк", "amount": 100},
            {"id": 2, "description": "Перевод ВТБ", "amount": 200},
            {"id": 3, "description": "Оплата услуг", "amount": 300},
        ]
        categories = ["Сбербанк", "ВТБ", "Оплата"]
        result = count_by_category(transactions, categories)

        assert result["Сбербанк"] == 1
        assert result["ВТБ"] == 1
        assert result["Оплата"] == 1

    def test_count_with_special_chars_in_description(self):
        """Тест подсчета с описаниями, содержащими специальные символы"""
        transactions = [
            {"id": 1, "description": "Перевод (срочный)", "amount": 100},
            {"id": 2, "description": "Пополнение-счета", "amount": 200},
            {"id": 3, "description": "Снятие/наличных", "amount": 300},
        ]
        categories = ["срочный", "Пополнение", "Снятие"]
        result = count_by_category(transactions, categories)

        assert result["срочный"] == 1
        assert result["Пополнение"] == 1
        assert result["Снятие"] == 1


@pytest.mark.parametrize(
    "search_word,expected_count",
    [
        ("перевод", 4),
        ("организации", 2),
        ("счета", 2),  # "Пополнение счета" и "Перевод со счета на счет"
        ("на", 3),  # "Снятие наличных" и "Перевод со счета на счет"
        ("test", 0),
        ("", 0),
    ],
)
def test_filter_parametrized(search_word, expected_count):
    """Параметризованный тест для filter_by_description"""
    result = filter_by_description(SAMPLE_TRANSACTIONS, search_word)
    assert len(result) == expected_count


@pytest.mark.parametrize(
    "categories,expected_counts",
    [
        (["Перевод организации", "Открытие вклада"], {"Перевод организации": 2, "Открытие вклада": 1}),
        (["перевод", "вклад"], {"перевод": 4, "вклад": 1}),
        (["несуществующая"], {"несуществующая": 0}),
    ],
)
def test_count_parametrized(categories, expected_counts):
    """Параметризованный тест для count_by_category"""
    result = count_by_category(SAMPLE_TRANSACTIONS, categories)
    assert result == expected_counts
