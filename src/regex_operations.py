import re
from collections import Counter
from typing import Dict, List


def filter_by_description(data: List[Dict], search: str) -> List[Dict]:
    """
    Фильтрует операции по строке поиска в описании.
    Использует регулярные выражения для поиска.
    """
    if not data or not search:
        return []

    filtered_data = []
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    for operation in data:
        description = operation.get("description", "")
        if pattern.search(description):
            filtered_data.append(operation)

    return filtered_data


def count_by_category(data: List[Dict], categories: List[str]) -> Dict[str, int]:
    """
    Считает количество операций по категориям.
    Использует Counter для подсчета.
    """
    if not data:
        return {category: 0 for category in categories} if categories else {}

    if not categories:
        return {}

    counter = Counter()

    # Считаем операции по категориям
    for operation in data:
        description = operation.get("description", "").lower()

        # Проверяем каждую категорию
        for category in categories:
            category_lower = category.lower()
            if category_lower in description:
                counter[category] += 1

    # Добавляем категории с нулевым количеством
    for category in categories:
        if category not in counter:
            counter[category] = 0

    return dict(counter)

