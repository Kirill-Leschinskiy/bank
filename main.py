from pathlib import Path
from typing import Dict, List, Optional

from src import processing, utils, widget
from src import file_loaders, regex_operations


def get_data_directory() -> Path:
    """
    Возвращает путь к папке с данными.
    Сначала ищет в текущей директории, затем в родительских.
    """
    # Пробуем несколько возможных расположений
    possible_paths = [
        Path("data"),  # Текущая директория
        Path("..") / "data",  # Родительская директория
        Path(__file__).parent / "data",  # Относительно main.py
        Path.cwd() / "data",  # Абсолютный путь
    ]

    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path.absolute()

    # Если папка не найдена, создаем в текущей директории
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir.absolute()


def find_data_file(data_dir: Path, file_type: str) -> Optional[Path]:
    """
    Ищет файл данных в указанной директории.
    """
    # Возможные имена файлов для каждого типа
    file_patterns = {
        "json": ["operations.json", "transactions.json", "data.json", "*.json"],
        "csv": ["transactions.csv", "operations.csv", "data.csv", "*.csv"],
        "xlsx": ["transaction_excel.xlsx", "transactions.xlsx", "operations.xlsx", "data.xlsx", "*.xlsx"]
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
                return files[0]
        else:
            # Ищем конкретный файл
            file_path = data_dir / pattern
            if file_path.exists():
                return file_path

    return None


def load_transactions_from_file(file_type: str) -> List[Dict]:
    """
    Загружает транзакции из файла.
    """
    print(f"\n📂 Загрузка данных из {file_type.upper()} файла...")

    # Находим папку с данными
    data_dir = get_data_directory()
    print(f"Папка с данными: {data_dir}")

    # Ищем файл
    file_path = find_data_file(data_dir, file_type)

    if not file_path:
        print(f"\n❌ Не найден {file_type.upper()} файл в папке {data_dir}")
        print("\nДоступные файлы:")
        files_found = False
        for item in data_dir.iterdir():
            if item.is_file():
                print(f"  - {item.name}")
                files_found = True

        if not files_found:
            print("  (папка пуста)")

        print(f"\nРекомендуемые имена файлов для формата {file_type.upper()}:")
        if file_type == "json":
            print("  - operations.json")
            print("  - transactions.json")
        elif file_type == "csv":
            print("  - transactions.csv")
            print("  - operations.csv")
        elif file_type == "xlsx":
            print("  - transaction_excel.xlsx")
            print("  - transactions.xlsx")

        return []

    print(f"✅ Найден файл: {file_path.name}")

    try:
        # Загружаем данные
        if file_type == "json":
            transactions = file_loaders.load_json(str(file_path))
        elif file_type == "csv":
            transactions = file_loaders.load_csv(str(file_path))
        elif file_type == "xlsx":
            transactions = file_loaders.load_xlsx(str(file_path))
        else:
            print(f"❌ Неподдерживаемый формат: {file_type}")
            return []

        if not transactions:
            print("⚠️  Файл загружен, но не содержит данных")
            return []

        # Нормализуем данные
        normalized_transactions = utils.normalize_transaction_data(transactions)

        print(f"✅ Успешно загружено {len(normalized_transactions)} транзакций")
        return normalized_transactions

    except FileNotFoundError:
        print(f"❌ Файл не найден: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла: {e}")
        return []


def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """
    Получает выбор пользователя с валидацией.
    """
    while True:
        print(prompt)
        choice = input("> ").strip()

        if choice in valid_choices:
            return choice
        else:
            print(f"❌ Неверный выбор. Допустимые значения: {', '.join(valid_choices)}")


def display_transactions(transactions: List[Dict]) -> None:
    """
    Отображает транзакции в удобном формате.
    """
    if not transactions:
        print("\n" + "=" * 60)
        print("❌ Нет транзакций для отображения")
        print("=" * 60)
        return

    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ПОИСКА: {len(transactions)} транзакций")
    print("=" * 60)

    for i, transaction in enumerate(transactions, 1):
        print(f"\n#{i}")

        # Дата
        try:
            date = widget.get_date(transaction.get("date", ""))
            description = transaction.get("description", "Без описания")
            print(f"📅 {date} {description}")
        except:
            print("📅 Дата недоступна")

        # От кого
        from_acc = transaction.get("from", "")
        if from_acc:
            try:
                print(f"   📤 Отправитель: {widget.mask_account_card(from_acc)}")
            except:
                print(f"   📤 Отправитель: {from_acc}")

        # Кому
        to_acc = transaction.get("to", "")
        if to_acc:
            try:
                print(f"   📥 Получатель: {widget.mask_account_card(to_acc)}")
            except:
                print(f"   📥 Получатель: {to_acc}")

        # Сумма
        op_amount = transaction.get("operationAmount", {})
        if isinstance(op_amount, dict):
            amount = op_amount.get("amount", "0")
            currency = op_amount.get("currency", {})

            if isinstance(currency, dict):
                code = currency.get("code", "RUB")
                name = currency.get("name", "")
            else:
                code = str(currency)
                name = str(currency)

            currency_symbol = "руб." if code == "RUB" else code
            print(f"   💰 Сумма: {amount} {currency_symbol}")

    print("\n" + "=" * 60)


def main() -> None:
    """Основная функция программы."""
    print("=" * 60)
    print("🏦 БАНКОВСКИЕ ТРАНЗАКЦИИ")
    print("=" * 60)

    # Выбор типа файла
    print("\nВыберите источник данных:")
    print("1. JSON файл")
    print("2. CSV файл")
    print("3. Excel файл")
    print("4. Выход")

    choice = get_user_choice("Введите номер (1-4):", ["1", "2", "3", "4"])

    if choice == "4":
        print("\n👋 До свидания!")
        return

    file_type_map = {"1": "json", "2": "csv", "3": "xlsx"}
    file_type = file_type_map[choice]

    # Загрузка данных
    transactions = load_transactions_from_file(file_type)

    if not transactions:
        print("\n❌ Не удалось загрузить данные. Завершение работы.")
        return

    # Фильтрация по статусу
    print("\n" + "=" * 50)
    print("ФИЛЬТРАЦИЯ ПО СТАТУСУ")
    print("=" * 50)

    status = get_user_choice(
        "Введите статус операции (EXECUTED, CANCELED, PENDING):",
        ["EXECUTED", "CANCELED", "PENDING"]
    )

    try:
        filtered = processing.filter_by_state(transactions, status)
        print(f"✅ Найдено {len(filtered)} операций со статусом {status}")
    except Exception as e:
        print(f"❌ Ошибка при фильтрации: {e}")
        return

    if not filtered:
        print("\n❌ Нет операций с выбранным статусом")
        return

    # Сортировка
    print("\nОтсортировать операции по дате?")
    sort_choice = get_user_choice("Введите Да/Нет:", ["Да", "Нет", "да", "нет", "Д", "Н", "д", "н"])

    if sort_choice.lower() in ["да", "д"]:
        order = get_user_choice(
            "Сортировать по возрастанию или убыванию?",
            ["возрастанию", "убыванию", "по возрастанию", "по убыванию"]
        )

        descending = "убыванию" in order.lower()
        try:
            filtered = processing.sort_by_date(filtered, descending)
            print(f"✅ Операции отсортированы по {'убыванию' if descending else 'возрастанию'}")
        except Exception as e:
            print(f"⚠️  Ошибка при сортировке: {e}")

    # Фильтрация по рублям
    print("\nВыводить только рублевые транзакции?")
    ruble_choice = get_user_choice("Введите Да/Нет:", ["Да", "Нет", "да", "нет", "Д", "Н", "д", "н"])

    if ruble_choice.lower() in ["да", "д"]:
        rub_transactions = []
        for trans in filtered:
            op_amount = trans.get("operationAmount", {})
            if isinstance(op_amount, dict):
                currency = op_amount.get("currency", {})
                if isinstance(currency, dict) and currency.get("code") == "RUB":
                    rub_transactions.append(trans)

        filtered = rub_transactions
        print(f"✅ Оставлено {len(filtered)} рублевых транзакций")

    # Поиск по описанию
    print("\nИскать по слову в описании?")
    search_choice = get_user_choice("Введите Да/Нет:", ["Да", "Нет", "да", "нет", "Д", "Н", "д", "н"])

    if search_choice.lower() in ["да", "д"]:
        search_word = input("Введите слово для поиска: ").strip()
        if search_word:
            result = regex_operations.filter_by_description(filtered, search_word)
            print(f"🔍 Найдено {len(result)} транзакций по слову '{search_word}'")
            filtered = result

    # Отображение результатов
    display_transactions(filtered[:10])  # Показываем первые 10

    # Статистика по категориям
    print("\nПоказать статистику по категориям?")
    stats_choice = get_user_choice("Введите Да/Нет:", ["Да", "Нет", "да", "нет", "Д", "Н", "д", "н"])

    if stats_choice.lower() in ["да", "д"] and filtered:
        # Определяем категории автоматически
        categories = []
        for trans in filtered:
            desc = trans.get("description", "")
            if "Перевод организации" in desc and "Перевод организации" not in categories:
                categories.append("Перевод организации")
            elif "Перевод с карты на карту" in desc and "Перевод с карты на карту" not in categories:
                categories.append("Перевод с карты на карту")
            elif "Перевод со счета на счет" in desc and "Перевод со счета на счет" not in categories:
                categories.append("Перевод со счета на счет")
            elif "Открытие вклада" in desc and "Открытие вклада" not in categories:
                categories.append("Открытие вклада")
            elif "Пополнение" in desc and "Пополнение" not in categories:
                categories.append("Пополнение")
            elif "Снятие" in desc and "Снятие" not in categories:
                categories.append("Снятие")

        if categories:
            stats = regex_operations.count_by_category(filtered, categories)
            print("\n📊 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
            print("-" * 30)
            for category, count in sorted(stats.items()):
                print(f"  {category}: {count} операций")
        else:
            print("ℹ️  Не удалось определить категории операций")

    print("\n" + "=" * 60)
    print("✅ ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()