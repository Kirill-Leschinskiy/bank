import re
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
    Возвращает словарь с количеством операций для каждой категории.
    """
    if not data:
        return {}

    categories_lower = [cat.lower() for cat in categories]
    result = {category: 0 for category in categories}

    for operation in data:
        description = operation.get("description", "").lower()
        for i, category in enumerate(categories_lower):
            if category in description:
                result[categories[i]] += 1
                break

    return result
