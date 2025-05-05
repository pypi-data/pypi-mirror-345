import unittest
from difflib import restore
from unittest import removeResult

from Logs import LoggerConfig
from NumWord import HumanizeNumber


class TestHumanizeNumber(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/Humanize_test.log").get_logger()
        cls.logger.info("TestHumanizeNumber started.")
        cls.humanize_num = HumanizeNumber()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestHumanizeNumber completed. \n -----------------")

    def test_thousand(self):
        result = self.humanize_num.convert(1000)
        self.logger.info(f"Test thousand: {result}")
        self.assertEqual(result, '1K')
        result = self.humanize_num.convert(10400)
        self.logger.info(f"Test thousand: {result}")
        self.assertEqual(result, '10.4K')
        result = self.humanize_num.convert(943672)
        self.logger.info(f"Test thousand: {result}")
        self.assertEqual(result, '943.67K')


    def test_trillion(self):
        result = self.humanize_num.convert(1000000000000)
        self.logger.info(f"Test trillion: {result}")
        self.assertEqual(result, '1T')
        result = self.humanize_num.convert(1040000000000)
        self.logger.info(f"Test trillion: {result}")
        self.assertEqual(result, '1.04T')
        result = self.humanize_num.convert(943678000000000)
        self.logger.info(f"Test trillion: {result}")
        self.assertEqual(result, '943.68T')

    def test_quadrillion(self):
        result = self.humanize_num.convert(1007834786334367)
        self.logger.info(f"Test quadrillion: {result}")
        self.assertEqual(result, '1.01Q')
        result = self.humanize_num.convert(1040046775700000)
        self.logger.info(f"Test quadrillion: {result}")
        self.assertEqual(result, '1.04Q')
        result = self.humanize_num.convert(9436780067482000)
        self.logger.info(f"Test quadrillion: {result}")
        self.assertEqual(result, '9.44Q')

    def test_kharab(self):
        result = self.humanize_num.convert(100000000000, lang='hi')
        self.logger.info(f"Test खरब: {result}")
        self.assertEqual(result, '1 खरब')
        result = self.humanize_num.convert(104000000000, lang='hi')
        self.logger.info(f"Test खरब: {result}")
        self.assertEqual(result, '1.04 खरब')
        result = self.humanize_num.convert(9436780000000, lang='hi')
        self.logger.info(f"Test खरब: {result}")
        self.assertEqual(result, '94.37 खरब')

    def test_Caror(self):
        result = self.humanize_num.convert(10000000, lang='hi')
        self.logger.info(f"Test करोड़: {result}")
        self.assertEqual(result, '1 करोड़')
        result = self.humanize_num.convert(10400000, lang='hi')
        self.logger.info(f"Test करोड़: {result}")
        self.assertEqual(result, '1.04 करोड़')
        result = self.humanize_num.convert(943678000, lang='hi')
        self.logger.info(f"Test करोड़: {result}")
        self.assertEqual(result, '94.37 करोड़')

    def test_Nil(self):
        result = self.humanize_num.convert(10000000000000, lang='hi')
        self.logger.info(f"Test नील: {result}")
        self.assertEqual(result, '1 नील')
        result = self.humanize_num.convert(10400000000000, lang='hi')
        self.logger.info(f"Test नील: {result}")
        self.assertEqual(result, '1.04 नील')
        result = self.humanize_num.convert(943678000000000, lang='hi')
        self.logger.info(f"Test नील: {result}")
        self.assertEqual(result, '94.37 नील')

    def test_Lakh(self):
        result = self.humanize_num.convert(100000, lang='en-hi')
        self.logger.info(f"Test Lakh: {result}")
        self.assertEqual(result, '1L')
        result = self.humanize_num.convert(104000, lang='en-hi')
        self.logger.info(f"Test Lakh: {result}")
        self.assertEqual(result, '1.04L')
        result = self.humanize_num.convert(9436780, lang='en-hi')
        self.logger.info(f"Test Lakh: {result}")
        self.assertEqual(result, '94.37L')

    def test_Madhya(self):
        result = self.humanize_num.convert(1000000000000000003480, lang='en-hi')
        self.logger.info(f"Test Madh: {result}")
        self.assertEqual(result, '1Madh')
        result = self.humanize_num.convert(1040000000000004324000, lang='en-hi')
        self.logger.info(f"Test Madh: {result}")
        self.assertEqual(result, '1.04Madh')
        result = self.humanize_num.convert(94367800000004230000000, lang='en-hi')
        self.logger.info(f"Test Madh: {result}")
        self.assertEqual(result, '94.37Madh')

    def test_million_to_lakh(self):
        result = self.humanize_num.convert("1.5M", 'en', 'hi')
        self.logger.info(f"Test humanize Million to लाख: 1.5M -> {result}" )
        self.assertEqual(result, "15 लाख")
        result = self.humanize_num.convert("1.5M", 'en', 'en-hi')
        self.logger.info(f"Test humanize Million to Lakh: 1.5M -> {result}")
        self.assertEqual(result, "15L")
        result = self.humanize_num.convert("1.5M", 'en-hi', 'en')
        self.logger.info(f"Test humanize Lakh to Million: 10L -> {result}")
        self.assertEqual(result, "1.5M")

    def test_not_matched(self):
        result = self.humanize_num.convert(100, 'en')
        self.logger.info(f"Test humanize 100 -> {result}")
        self.assertEqual(result, "100")


if __name__ == '__main__':
    unittest.main()
