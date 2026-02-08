from typing import Dict, List, Union


def filter_by_state(
        banking_operations: List[Dict[str, Union[str, int]]],
        state: str = "EXECUTED"
) -> List[Dict[str, str | int]]:
    """
    Функция фильтрует операции по статусу.
    Оптимизирована для работы с большими наборами данных.
    """
    if not isinstance(banking_operations, list):
        raise TypeError("banking_operations должен быть списком")

    if not banking_operations:
        raise ValueError("Передан пустой список")

    if not isinstance(state, str):
        raise TypeError("state должен быть строкой")

    # Приводим искомый статус к верхнему регистру
    target_state = state.upper().strip()

    banking_operations_filtered = []

    for operation in banking_operations:
        if not isinstance(operation, dict):
            continue  # Пропускаем некорректные записи

        # Получаем значение state из операции
        # Пробуем разные варианты ключа (на случай разных регистров)
        op_state_value = None

        # Сначала проверяем 'state' (нижний регистр, как нормализуется в utils)
        if 'state' in operation:
            op_state_value = operation['state']
        # Затем проверяем другие возможные варианты
        elif 'State' in operation:
            op_state_value = operation['State']
        elif 'STATE' in operation:
            op_state_value = operation['STATE']

        if op_state_value is None:
            continue  # Нет поля state

        # Приводим значение state к строке и верхнему регистру
        try:
            if isinstance(op_state_value, str):
                current_state = op_state_value.upper().strip()
            else:
                current_state = str(op_state_value).upper().strip()

            # Сравниваем с искомым статусом
            if current_state == target_state:
                banking_operations_filtered.append(operation)
        except (AttributeError, TypeError):
            # Если не можем преобразовать, пропускаем
            continue

    return banking_operations_filtered


def sort_by_date(
        banking_operations: List[Dict[str, Union[str, int]]],
        descending_sort: bool = True
) -> List[Dict[str, str | int]]:
    """Функция сортирует операции по дате"""
    if not isinstance(banking_operations, list):
        raise TypeError("banking_operations должен быть списком")

    if not banking_operations:
        raise ValueError("Передан пустой список")

    if not isinstance(descending_sort, bool):
        raise TypeError("descending_sort должен быть булевым значением")

    # Разделяем операции с датой и без
    with_date = []
    without_date = []

    for i, operation in enumerate(banking_operations):
        if not isinstance(operation, dict):
            continue

        date_str = operation.get("date")
        if date_str and isinstance(date_str, str):
            with_date.append((date_str, i, operation))
        else:
            without_date.append(operation)

    # Сортируем операции с датой
    with_date.sort(key=lambda x: x[0], reverse=descending_sort)

    # Собираем результат
    result = [op for _, _, op in with_date]
    result.extend(without_date)

    return result
