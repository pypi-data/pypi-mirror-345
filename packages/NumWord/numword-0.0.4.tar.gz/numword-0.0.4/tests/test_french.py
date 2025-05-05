import unittest

from Logs import LoggerConfig
from NumWord import WordToNumber, NumberToWord


class TestWordToNum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/French_test.log").get_logger()
        cls.logger.info("TestWordToNum (French) started.")
        cls.word_to_num = WordToNumber()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestWordToNum (French) completed. \n -----------------")

    def test_single_digit(self):
        result = self.word_to_num.convert("six", lang='fr')
        self.logger.info(f"Test single digit: 'six' -> {result}")
        self.assertEqual(result, 6)

    def test_two_digits(self):
        result = self.word_to_num.convert("vingt-et-un", lang='fr')
        self.logger.info(f"Test two digits: 'vingt-et-un' -> {result}")
        self.assertEqual(result, 21)

    def test_negative_number(self):
        result = self.word_to_num.convert("moins mille deux cent trente-quatre", lang='fr')
        self.logger.info(f"Test negative number: 'moins mille deux cent trente-quatre' -> {result}")
        self.assertEqual(result, -1234)

    def test_large_number(self):
        result = self.word_to_num.convert("mille deux cent trente-quatre", lang='fr')
        self.logger.info(f"Test large number: 'mille deux cent trente-quatre' -> {result}")
        self.assertEqual(result, 1234)

    def test_decimal_number(self):
        result = self.word_to_num.convert("un virgule cinq", lang='fr')
        self.logger.info(f"Test decimal number: 'un virgule cinq' -> {result}")
        self.assertEqual(result, 1.5)

    def test_mixed_number(self):
        result = self.word_to_num.convert("cent vingt-trois virgule quatre cinq six", lang='fr')
        self.logger.info(f"Test mixed number: 'cent vingt-trois virgule quatre cinq six' -> {result}")
        self.assertEqual(result, 123.456)

    def test_million_number(self):
        result = self.word_to_num.convert("dix million", lang='fr')
        self.logger.info(f"Test million number: 'dix million' -> {result}")
        self.assertEqual(result, 10000000)

    def test_invalid_word(self):
        with self.assertRaises(ValueError):
            self.word_to_num.convert("invalide", lang='fr')

    def test_billion(self):
        result = self.word_to_num.convert("un billion", lang='fr')
        self.logger.info(f"Test billion: 'un billion' -> {result}")
        self.assertEqual(result, 1000000000000)


class TestNumToWord(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/French_test.log").get_logger()
        cls.logger.info("TestNumToWord (French) started.")
        cls.num_to_word = NumberToWord()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestNumToWord (French) completed. \n -----------------")

    def test_single_digit(self):
        result = self.num_to_word.convert(6, lang='fr')
        self.logger.info(f"Test single digit: 6 -> {result}")
        self.assertEqual(result, "six")

    def test_two_digits(self):
        result = self.num_to_word.convert(21, lang='fr')
        self.logger.info(f"Test two digits: 21 -> {result}")
        self.assertEqual(result, "vingt-et-un")

    def test_negative_number(self):
        result = self.num_to_word.convert(-1234, lang='fr')
        self.logger.info(f"Test negative number: -1234 -> {result}")
        self.assertEqual(result, "moins un mille deux cent trente-quatre")

    def test_large_number(self):
        result = self.num_to_word.convert(1234, lang='fr')
        self.logger.info(f"Test large number: 1234 -> {result}")
        self.assertEqual(result, "un mille deux cent trente-quatre")

    def test_decimal_number(self):
        result = self.num_to_word.convert(1.5, lang='fr')
        self.logger.info(f"Test decimal number: 1.5 -> {result}")
        self.assertEqual(result, "un virgule cinq")

    def test_mixed_number(self):
        result = self.num_to_word.convert(123.456, lang='fr')
        self.logger.info(f"Test mixed number: 123.456 -> {result}")
        self.assertEqual(result, "un cent vingt-trois virgule quatre cinq six")

    def test_million_number(self):
        result = self.num_to_word.convert(10000000, lang='fr')
        self.logger.info(f"Test million number: 10000000 -> {result}")
        self.assertEqual(result, "dix million")


if __name__ == '__main__':
    unittest.main()
