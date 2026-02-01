import os
from typing import Dict, List

from src import generators, processing, widget, utils
from src import file_loaders, regex_operations


def load_transactions_from_file(file_type: str = "json") -> List[Dict]:
    """
    Загружает и нормализует транзакции из файла.
    """
    print(f"Попытка загрузки {file_type.upper()} файла...")

    # Загружаем данные
    transactions = file_loaders.load_transactions(file_type)

    if not transactions:
        print(f"Не удалось загрузить данные из {file_type.upper()} файла")
        return []

    # Нормализуем структуру данных
    normalized_transactions = utils.normalize_transaction_data(transactions)

    print(f"Успешно загружено {len(normalized_transactions)} транзакций")
    return normalized_transactions


def get_valid_status() -> str:
    """Получает валидный статус операции от пользователя."""
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        print("\n" + "=" * 50)
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
        status = input("> ").strip().upper()

        if not status:
            print("Статус не может быть пустым.")
            continue

        if status in valid_statuses:
            return status
        else:
            print(f'Статус операции "{status}" недоступен.')


def get_yes_no_choice(prompt: str) -> bool:
    """Получает ответ Да/Нет от пользователя."""
    while True:
        print(prompt)
        choice = input("Введите Да или Нет: ").lower().strip()

        if choice in ["да", "д", "yes", "y"]:
            return True
        elif choice in ["нет", "н", "no", "n"]:
            return False
        else:
            print("❌ Пожалуйста, введите 'Да' или 'Нет'")


def format_transaction_output(transaction: Dict) -> str:
    """Форматирует транзакцию для вывода в консоль."""
    output_lines = []

    # Дата
    try:
        date_str = widget.get_date(transaction.get("date", ""))
        description = transaction.get("description", "Без описания")
        output_lines.append(f"📅 {date_str} {description}")
    except Exception as e:
        output_lines.append(f"📅 Дата недоступна")

    # Отправитель
    from_account = transaction.get("from", "")
    to_account = transaction.get("to", "")

    if from_account and to_account:
        try:
            masked_from = widget.mask_account_card(from_account)
            masked_to = widget.mask_account_card(to_account)
            output_lines.append(f"   📤 {masked_from}")
            output_lines.append(f"   📥 {masked_to}")
        except Exception as e:
            output_lines.append(f"   📤 {from_account}")
            output_lines.append(f"   📥 {to_account}")
    elif from_account:
        try:
            masked_from = widget.mask_account_card(from_account)
            output_lines.append(f"   📤 Отправитель: {masked_from}")
        except:
            output_lines.append(f"   📤 Отправитель: {from_account}")
    elif to_account:
        try:
            masked_to = widget.mask_account_card(to_account)
            output_lines.append(f"   📥 Получатель: {masked_to}")
        except:
            output_lines.append(f"   📥 Получатель: {to_account}")

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

        # Определяем символ валюты
        if currency_code == "RUB":
            currency_symbol = "₽"
        elif currency_code == "USD":
            currency_symbol = "$"
        elif currency_code == "EUR":
            currency_symbol = "€"
        else:
            currency_symbol = currency_code

        output_lines.append(f"   💰 Сумма: {amount} {currency_symbol}")

    return "\n".join(output_lines)


def process_bank_search_interactive(data: List[Dict]) -> List[Dict]:
    """Интерактивная функция поиска по описанию."""
    if not data:
        return []

    if get_yes_no_choice("\nОтфильтровать список транзакций по определенному слову в описании?"):
        search_word = input("Введите слово для поиска в описании: ").strip()
        if search_word:
            original_count = len(data)
            data = regex_operations.filter_by_description(data, search_word)
            print(f"🔍 Найдено {len(data)} транзакций по слову '{search_word}' "
                  f"(было {original_count})")
        else:
            print("Слово для поиска не введено, пропускаем фильтрацию.")

    return data


def display_transactions(transactions: List[Dict], max_display: int = 10):
    """Отображает транзакции с нумерацией."""
    if not transactions:
        print("\n" + "=" * 50)
        print("❌ Не найдено транзакций для отображения")
        return

    print("\n" + "=" * 50)
    print(f"📊 Всего банковских операций в выборке: {len(transactions)}")
    print("=" * 50)

    display_count = min(len(transactions), max_display)
    for i, transaction in enumerate(transactions[:display_count], 1):
        print(f"\n#{i}")
        print(format_transaction_output(transaction))

    if len(transactions) > display_count:
        print(f"\n... и еще {len(transactions) - display_count} транзакций "
              f"(показано {display_count})")


def show_category_statistics(transactions: List[Dict]):
    """Показывает статистику по категориям операций."""
    if not transactions:
        print("Нет данных для статистики")
        return

    # Автоматически определяем категории из описаний
    categories_set = set()
    for transaction in transactions:
        desc = transaction.get("description", "").lower()
        if "перевод организации" in desc:
            categories_set.add("Перевод организации")
        elif "перевод с карты на карту" in desc:
            categories_set.add("Перевод с карты на карту")
        elif "перевод со счета на счет" in desc:
            categories_set.add("Перевод со счета на счет")
        elif "открытие вклада" in desc:
            categories_set.add("Открытие вклада")
        elif "пополнение" in desc:
            categories_set.add("Пополнение")
        elif "снятие" in desc:
            categories_set.add("Снятие наличных")
        elif "перевод" in desc:
            categories_set.add("Перевод")

    categories = list(categories_set)

    if categories:
        stats = regex_operations.count_by_category(transactions, categories)
        print("\n📈 Статистика по категориям операций:")
        print("-" * 30)
        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {category}: {count} операций")
    else:
        print("Не удалось определить категории операций")


def main():
    """Основная функция программы."""
    print("=" * 60)
    print("🏦 БАНКОВСКИЕ ТРАНЗАКЦИИ - АНАЛИЗ И ФИЛЬТРАЦИЯ")
    print("=" * 60)

    # Выбор типа файла
    print("\nВыберите источник данных:")
    print("1. JSON файл (operations.json)")
    print("2. CSV файл (transactions.csv)")
    print("3. Excel файл (transaction_excel.xlsx)")
    print("4. Выход")

    file_choice = input("\nВведите номер выбора: ").strip()

    file_type = None
    if file_choice == "1":
        file_type = "json"
        print("\n✅ Выбран JSON файл")
    elif file_choice == "2":
        file_type = "csv"
        print("\n✅ Выбран CSV файл")
    elif file_choice == "3":
        file_type = "xlsx"
        print("\n✅ Выбран Excel файл")
    elif file_choice == "4":
        print("\n👋 До свидания!")
        return
    else:
        print("\n⚠️  Неверный выбор. Используется JSON по умолчанию.")
        file_type = "json"

    # Загрузка данных
    print("\n" + "-" * 40)
    print("📂 ЗАГРУЗКА ДАННЫХ...")

    transactions = load_transactions_from_file(file_type)

    if not transactions:
        print("❌ Не удалось загрузить данные. Проверьте наличие файлов в папке 'data/'")
        print("Структура папки data/:")
        for root, dirs, files in os.walk("data"):
            for file in files:
                print(f"  - {file}")
        return

    # Фильтрация по статусу
    print("\n" + "-" * 40)
    print("🎯 ФИЛЬТРАЦИЯ ПО СТАТУСУ")
    status = get_valid_status()

    filtered_transactions = processing.filter_by_state(transactions, status)
    print(f"✅ Найдено {len(filtered_transactions)} операций со статусом '{status}'")

    if not filtered_transactions:
        print("\n❌ Не найдено транзакций с выбранным статусом")
        return

    # Сортировка по дате
    print("\n" + "-" * 40)
    print("📅 СОРТИРОВКА")

    if get_yes_no_choice("Отсортировать операции по дате?"):
        while True:
            print("\nВыберите порядок сортировки:")
            print("1. По убыванию (новые сначала)")
            print("2. По возрастанию (старые сначала)")
            sort_choice = input("Введите номер: ").strip()

            if sort_choice == "1":
                descending = True
                print("📉 Сортировка по убыванию (новые сначала)")
                break
            elif sort_choice == "2":
                descending = False
                print("📈 Сортировка по возрастанию (старые сначала)")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")

        filtered_transactions = processing.sort_by_date(filtered_transactions, descending)

    # Фильтрация по валюте
    print("\n" + "-" * 40)
    print("💱 ФИЛЬТРАЦИЯ ПО ВАЛЮТЕ")

    if get_yes_no_choice("Выводить только рублевые транзакции?"):
        rub_transactions = []
        for transaction in filtered_transactions:
            operation_amount = transaction.get("operationAmount", {})
            if isinstance(operation_amount, dict):
                currency = operation_amount.get("currency", {})
                if isinstance(currency, dict) and currency.get("code") == "RUB":
                    rub_transactions.append(transaction)

        filtered_transactions = rub_transactions
        print(f"✅ Оставлено {len(filtered_transactions)} рублевых транзакций")

    # Поиск по описанию
    filtered_transactions = process_bank_search_interactive(filtered_transactions)

    # Вывод результатов
    if not filtered_transactions:
        print("\n" + "=" * 60)
        print("❌ Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        print("=" * 60)
        return

    # Отображение транзакций
    display_transactions(filtered_transactions)

    # Дополнительные опции
    print("\n" + "-" * 40)
    print("📊 ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ")

    if get_yes_no_choice("Показать статистику по категориям операций?"):
        show_category_statistics(filtered_transactions)

    # Демонстрация генераторов
    print("\n" + "-" * 40)
    print("🔄 ДЕМОНСТРАЦИЯ ГЕНЕРАТОРОВ")

    if get_yes_no_choice("Показать пример работы генераторов?"):
        print("\n🔢 Генератор номеров банковских карт:")
        for i, card_num in enumerate(generators.card_number_generator(1000, 1005), 1):
            print(f"  {i}. {card_num}")

        print("\n📝 Генератор описаний транзакций:")
        descriptions = generators.transaction_descriptions(filtered_transactions[:3])
        for i, desc in enumerate(descriptions, 1):
            print(f"  {i}. {desc}")

        print("\n💵 Генератор транзакций в USD:")
        usd_transactions = generators.filter_by_currency(filtered_transactions, "USD")
        usd_list = list(usd_transactions)[:3]
        if usd_list:
            for i, trans in enumerate(usd_list, 1):
                desc = trans.get("description", "Без описания")
                print(f"  {i}. {desc}")
        else:
            print("  Нет транзакций в USD")

    # Конвертация в рубли (демонстрация)
    print("\n" + "-" * 40)
    if get_yes_no_choice("Конвертировать суммы транзакций в рубли (демо)?"):
        try:
            from src.external_api import convert_to_rub
            print("\n💱 Конвертация в рубли (требуется API ключ):")
            for i, transaction in enumerate(filtered_transactions[:2], 1):
                try:
                    amount_in_rub = convert_to_rub(transaction)
                    print(f"  Транзакция {i}: {amount_in_rub} руб.")
                except Exception as e:
                    print(f"  Транзакция {i}: Ошибка конвертации - {e}")
        except Exception as e:
            print(f"  Ошибка при попытке конвертации: {e}")

    print("\n" + "=" * 60)
    print("✅ РАБОТА ПРОГРАММЫ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("Проверьте логи в папке logs/ для подробной информации")