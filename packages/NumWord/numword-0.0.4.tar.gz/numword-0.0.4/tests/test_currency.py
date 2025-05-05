import unittest

from Logs import LoggerConfig
from NumWord import Currency
import os


class TestCurrency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/Currency_test.log").get_logger()
        cls.logger.info("TestCurrency started.")
        cls.currency = Currency()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestCurrency completed. \n -----------------")

    def test_currency_conversion_valid(self):
        result = self.currency.convert(100, "USD", "EUR", with_symbol=False)
        self.assertIsInstance(result, str)
        self.logger.info(f"Test Convert 100 USD to EUR without symbol -> {result}")
        self.assertTrue("EUR" in result)

        result = self.currency.convert(50, "EUR", "INR", with_symbol=True)
        self.assertIsInstance(result, str)
        self.logger.info(f"Test Convert 50 EUR to INR with symbol -> {result}")
        self.assertTrue("₹" in result)

    def test_invalid_currency(self):
        self.logger.info("Test Invalid Currency Code")
        with self.assertRaises(ValueError):
            self.currency.convert(100, "USD", "XYZ", with_symbol=True)  # Invalid currency code

    def test_load_exchange_rates_from_file(self):
        rates = self.currency._Currency__rates
        self.assertIsInstance(rates, dict)
        self.logger.info(f"Test Exchange rates load successfully: Total rates found -> {len(rates)}")
        self.assertGreater(len(rates), 0)

    def test_fetch_exchange_rates(self):
        data = self.currency._Currency__fetch_exchange_rates()
        self.logger.info(f"Test Base Code is USD -> {data['Base']}")
        self.assertEqual(data["Base"], "USD")
        self.assertGreater(len(data["rates"]), 0)

    def test_currency_conversion_with_live_data(self):
        self.logger.info(f"Test Cases with live exchange rates")
        result = self.currency.convert(100, "USD", "EUR", with_symbol=False)
        self.assertIsInstance(result, str)
        self.assertTrue("EUR" in result)

        result = self.currency.convert(100, "USD", "EUR", with_symbol=True)
        self.assertIsInstance(result, str)
        self.assertTrue("€" in result)


if __name__ == '__main__':
    unittest.main()
