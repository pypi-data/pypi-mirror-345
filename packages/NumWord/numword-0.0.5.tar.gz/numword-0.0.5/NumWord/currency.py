import os
import json
import requests
from datetime import datetime

from utility.symboles import CURRENCY_SYMBOLS


class Currency:
    __FILE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utility', 'exchange_rates.json')
    __BASE_CURRENCY = "USD"

    def __init__(self):
        self.__load_or_update_rates()

    def __fetch_exchange_rates(self):
        """
        Fetch all exchange rates for the base currency from an API.

        Returns:
            dict: A dictionary containing the date, rates, and base currency.

        Raises:
            ConnectionError: If the API request fails or returns an error.
        """
        url = f"https://open.er-api.com/v6/latest/{self.__BASE_CURRENCY}"
        response = requests.get(url)
        format_data = {}
        if response.status_code == 200:
            data = response.json()
            format_data["date"] = datetime.now().strftime("%Y-%m-%d")
            format_data["rates"] = data["rates"]
            format_data["Base"] = data["base_code"]
            return format_data
        else:
            raise ConnectionError("Failed to fetch exchange rates")

    def __save_exchange_rates(self, data):
        """
        Save exchange rates to a JSON file.

        Args:
            data (dict): The exchange rates data to be saved.
        """
        with open(self.__FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def __load_exchange_rates(self):
        """
        Load exchange rates from file if valid.

        Returns:
            dict|None: The loaded exchange rates data if valid, or `None` if not valid.
        """
        if os.path.exists(self.__FILE_NAME):
            with open(self.__FILE_NAME, "r") as file:
                data = json.load(file)
                if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    return data
        return None

    def __load_or_update_rates(self):
        """
        Load exchange rates from file or update them by fetching from the API.
        """
        data = self.__load_exchange_rates()
        if data is None:
            data = self.__fetch_exchange_rates()
            self.__save_exchange_rates(data)
        self.__rates = data["rates"]

    def __get_exchange_rate(self, from_currency, to_currency):
        """
        Get exchange rate from stored data.
        """
        from_rate = self.__rates.get(from_currency)
        to_rate = self.__rates.get(to_currency)

        if from_currency == self.__BASE_CURRENCY:
            if to_rate is None:
                return None
            return to_rate

        elif to_currency == self.__BASE_CURRENCY:
            if from_rate is None:
                return None
            return 1 / from_rate

        if from_rate is None or to_rate is None:
            return None

        return to_rate / from_rate

    def convert(self, amount, from_currency, to_currency, with_symbol=True):
        """
        Convert an amount from one currency to another.
        """
        invalid_currencies = []
        if from_currency not in self.__rates:
            invalid_currencies.append(from_currency)
        if to_currency not in self.__rates:
            invalid_currencies.append(to_currency)

        if invalid_currencies:
            raise ValueError(f"Invalid currency code(s): {', '.join(invalid_currencies)}")

        rate = self.__get_exchange_rate(from_currency, to_currency)

        converted_amount = amount * rate

        if with_symbol:
            symbol = CURRENCY_SYMBOLS.get(to_currency)
            if not symbol:
                raise ValueError(f"Currency symbol not found for '{to_currency}'")
            return f'{symbol} {converted_amount:.2f}'
        else:
            return f'{converted_amount:.2f} {to_currency}'

