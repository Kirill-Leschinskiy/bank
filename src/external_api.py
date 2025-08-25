import os

import requests
from dotenv import load_dotenv

load_dotenv()


def convert_to_rub(transaction: dict) -> float:
    """Конвертирует сумму транзакции в рубли"""
    amount = transaction["amount"]
    currency = transaction["currency"]

    if currency == "RUB":
        return float(amount)

    url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount={amount}"
    headers = {"apikey": os.getenv("API_KEY")}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return float(response.json()["result"])
    else:
        return float(amount)
