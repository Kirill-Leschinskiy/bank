from typing import Dict, List, Union


def filter_by_state(
    banking_operations: List[Dict[str, Union[str, int]]], state: str = "EXECUTED"
) -> List[Dict[str, str | int]]:
    """Функция фильтрует операции по статусу"""
    if banking_operations == []:
        raise ValueError("Передан пустой список")
    banking_operations_filtered = []
    for operation in banking_operations:
        if operation.get("state") == state:
            banking_operations_filtered.append(operation)
    return banking_operations_filtered


def sort_by_date(
    banking_operations: List[Dict[str, Union[str, int]]], descending_sort: bool = True
) -> List[Dict[str, str | int]]:
    """Функция сортирует операции по дате (сначала самые последние)"""
    if banking_operations == []:
        raise ValueError("Передан пустой список")
    banking_operations_sorted = []
    dates = []
    for operation in banking_operations:
        if operation.get("date"):
            dates.append(operation["date"])
    dates.sort(reverse=descending_sort)
    for date in dates:
        for operation in banking_operations:
            if operation.get("date") == date:
                if operation not in banking_operations_sorted:
                    banking_operations_sorted.append(operation)
    return banking_operations_sorted
