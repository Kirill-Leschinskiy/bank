import sys
from pathlib import Path
from typing import Dict, List, Optional

from src import processing, utils, widget
from src import file_loaders, regex_operations


def find_data_file(file_type: str) -> Optional[Path]:
    """
    Ищет файл данных в папке data/ с различными вариантами имен.
    """
    data_dir = Path("data")

    if not data_dir.exists():
        print(f"Папка 'data/' не найдена.")
        print("Создайте папку 'data/' в той же директории, где находится main.py")
        print(f"Текущая директория: {Path.cwd()}")
        return None

    # Возможные имена файлов для каждого типа
    file_patterns = {
        "json": ["operations.json", "transactions.json", "*.json"],
        "csv": ["transactions.csv", "operations.csv", "*.csv"],
        "xlsx": ["transaction_excel.xlsx", "transactions.xlsx", "operations.xlsx", "*.xlsx"]
    }

    file_type = file_type.lower()
    if file_type not in file_patterns:
        return None

    # Сначала ищем по конкретным именам
    for pattern in file_patterns[file_type]:
        if "*" in pattern:
            # Ищем по шаблону
            files = list(data_dir.glob(pattern))
            if files:
                print(f"Найден файл по шаблону: {files[0].name}")
                return files[0]
        else:
            # Ищем конкретный файл
            file_path = data_dir / pattern
            if file_path.exists():
                print(f"Найден файл: {file_path.name}")
                return file_path

    # Если файл не найден, покажем что есть в папке
    print(f"Не найден {file_type.upper()} файл в папке data/")
    print("\nСодержимое папки data/:")

    files_found = False
    for item in data_dir.iterdir():
        if item.is_file():
            print(f"   {item.name}")
            files_found = True

    if not files_found:
        print("  (папка пуста)")

    return None


def load_transactions_from_file(file_type: str) -> List[Dict]:
    """
    Загружает транзакции из файла.
    """
    print(f"\nДля обработки выбран {file_type.upper()}-файл.")

    file_path = find_data_file(file_type)

    try:
        if file_type == "json":
            transactions = file_loaders.load_json(str(file_path))
        elif file_type == "csv":
            transactions = file_loaders.load_csv(str(file_path))
        elif file_type == "xlsx":
            transactions = file_loaders.load_xlsx(str(file_path))
        else:
            return []

        if not transactions:
            print("Файл пуст или не содержит данных")
            return []

        # Нормализуем данные
        normalized_transactions = utils.normalize_transaction_data(transactions)
        return normalized_transactions

    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return []
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return []


def get_valid_status() -> str:
    """
    Получает валидный статус операции от пользователя.
    """
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        print("\n" + "=" * 50)
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")

        user_input = input("> ").strip()

        if not user_input:
            print("Статус не может быть пустым.")
            continue

        status = user_input.upper()

        if status in valid_statuses:
            print(f"Операции отфильтрованы по статусу \"{status}\"\n")
            return status
        else:
            print(f'Статус операции "{user_input}" недоступен.')


def get_yes_no_answer(prompt: str) -> bool:
    """
    Получает ответ Да/Нет от пользователя.
    """
    while True:
        print(prompt)
        answer = input("> ").strip().lower()

        if answer in ["да", "д", "yes", "y"]:
            return True
        elif answer in ["нет", "н", "no", "n"]:
            return False
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'\n")


def get_sort_order() -> bool:
    """
    Получает порядок сортировки от пользователя.
    Возвращает True для убывания (новые сначала), False для возрастания.
    """
    while True:
        print("Отсортировать по возрастанию или по убыванию?")
        order = input("> ").strip().lower()

        if "возр" in order or "стар" in order:
            print("Сортировка по возрастанию (старые сначала)\n")
            return False
        elif "убыв" in order or "нов" in order:
            print("Сортировка по убыванию (новые сначала)\n")
            return True
        else:
            print("Пожалуйста, укажите 'по возрастанию' или 'по убыванию'\n")


def format_transaction_for_display(transaction: Dict) -> str:
    """
    Форматирует транзакцию для вывода в соответствии с требованиями.
    """
    lines = []

    # Дата
    try:
        date_str = widget.get_date(transaction.get("date", ""))
        description = transaction.get("description", "")
        lines.append(f"{date_str} {description}")
    except:
        lines.append("Дата недоступна")

    # Отправитель и получатель
    from_account = transaction.get("from", "")
    to_account = transaction.get("to", "")

    if from_account and to_account:
        try:
            masked_from = widget.mask_account_card(from_account)
            masked_to = widget.mask_account_card(to_account)

            # Форматируем согласно примеру из задания
            if "счет" in from_account.lower() and "счет" in to_account.lower():
                lines.append(f"{masked_from} -> {masked_to}")
            elif "счет" in from_account.lower():
                lines.append(f"{masked_from} ->")
                lines.append(f"{masked_to}")
            elif "счет" in to_account.lower():
                lines.append(f"{masked_from} ->")
                lines.append(f"{masked_to}")
            else:
                # Карта -> Карта
                lines.append(f"{masked_from} -> {masked_to}")

        except Exception as e:
            print(f"Ошибка при форматировании: {e}")
            lines.append(f"{from_account} -> {to_account}")
    else:
        if from_account:
            try:
                lines.append(widget.mask_account_card(from_account))
            except:
                lines.append(from_account)
        if to_account:
            try:
                lines.append(widget.mask_account_card(to_account))
            except:
                lines.append(to_account)

    # Сумма
    operation_amount = transaction.get("operationAmount", {})
    if isinstance(operation_amount, dict):
        amount = operation_amount.get("amount", "0")
        currency = operation_amount.get("currency", {})

        if isinstance(currency, dict):
            currency_code = currency.get("code", "RUB")
            currency_name = currency.get("name", "")
        else:
            currency_code = str(currency)
            currency_name = str(currency)

        # Определяем отображение валюты
        if currency_code == "RUB":
            currency_display = "руб."
        elif currency_code == "USD":
            currency_display = "USD"
        elif currency_code == "EUR":
            currency_display = "EUR"
        else:
            currency_display = currency_name

        lines.append(f"Сумма: {amount} {currency_display}")

    return "\n".join(lines)


def display_transactions(transactions: List[Dict]) -> None:
    """
    Отображает транзакции в требуемом формате.
    """
    if not transactions:
        print("\n" + "=" * 60)
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        print("=" * 60)
        return

    print("\n" + "=" * 60)
    print("Распечатываю итоговый список транзакций...")
    print("=" * 60)
    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")

    for i, transaction in enumerate(transactions, 1):
        print(format_transaction_for_display(transaction))
        print()  # Пустая строка между транзакциями


def main() -> None:
    """Основная функция программы."""
    print("=" * 60)
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")
    print("=" * 60)

    # Выбор типа файла
    while True:
        try:
            choice = input("> ").strip()

            if choice == "1":
                file_type = "json"
                break
            elif choice == "2":
                file_type = "csv"
                break
            elif choice == "3":
                file_type = "xlsx"
                break
            else:
                print("Неверный выбор. Введите 1, 2, 3\n")
        except EOFError:
            print("\nПрограмма завершена")
            return
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана")
            return

    # Загрузка данных
    transactions = load_transactions_from_file(file_type)

    if not transactions:
        return

    # Фильтрация по статусу
    status = get_valid_status()
    filtered_transactions = processing.filter_by_state(transactions, status)

    if not filtered_transactions:
        print("Не найдено операций с выбранным статусом")

        # Покажем какие статусы есть в данных
        unique_states = set()
        for transaction in transactions:
            state = transaction.get('state')
            if state:
                unique_states.add(state)

        if unique_states:
            print(f"\nДоступные статусы в данных: {', '.join(sorted(unique_states))}")

        return

    # Сортировка по дате
    if get_yes_no_answer("Отсортировать операции по дате? Да/Нет"):
        sort_descending = get_sort_order()
        filtered_transactions = processing.sort_by_date(filtered_transactions, sort_descending)

    # Фильтрация по рублевым транзакциям
    if get_yes_no_answer("Выводить только рублевые транзакции? Да/Нет"):
        ruble_transactions = []
        for transaction in filtered_transactions:
            operation_amount = transaction.get("operationAmount", {})
            if isinstance(operation_amount, dict):
                currency = operation_amount.get("currency", {})
                if isinstance(currency, dict) and currency.get("code") == "RUB":
                    ruble_transactions.append(transaction)

        filtered_transactions = ruble_transactions
        if filtered_transactions:
            print(f"Оставлено {len(filtered_transactions)} рублевых транзакций\n")
        else:
            print("⚠Рублевых транзакций не найдено\n")

    # Поиск по описанию
    if get_yes_no_answer("Отфильтровать список транзакций по определенному слову в описании? Да/Нет"):
        search_word = input("Введите слово для поиска: ").strip()
        if search_word:
            search_results = regex_operations.filter_by_description(filtered_transactions, search_word)
            print(f"Найдено {len(search_results)} транзакций по слову '{search_word}'\n")
            filtered_transactions = search_results

    # Отображение результатов
    display_transactions(filtered_transactions[:50])  # Ограничиваем вывод

    print("\n" + "=" * 60)
    print("Работа программы завершена успешно!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)