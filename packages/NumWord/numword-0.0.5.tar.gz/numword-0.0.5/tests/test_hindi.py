import unittest

from Logs import LoggerConfig
from NumWord import WordToNumber, NumberToWord


class TestWordToNum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/Hindi_test.log").get_logger()
        cls.logger.info("TestWordToNum started.")
        cls.word_to_num = WordToNumber()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestWordToNum completed. \n -----------------")

    def test_single_digit(self):
        result = self.word_to_num.convert("छह", lang='hi')
        self.logger.info(f"Test single digit: 'छह' -> {result}")
        self.assertEqual(result, 6)

    def test_two_digits(self):
        result = self.word_to_num.convert("इक्कीस", lang='hi')
        self.logger.info(f"Test two digits: 'इक्कीस' -> {result}")
        self.assertEqual(result, 21)

    def test_negative_number(self):
        result = self.word_to_num.convert("एक हजार दो सौ चौंतीस", lang='hi')
        self.logger.info(f"Test negative number: 'एक हजार दो सौ चौंतीस' -> {result}")
        self.assertEqual(result, 1234)

    def test_large_number(self):
        result = self.word_to_num.convert("एक हजार दो सौ चौंतीस", lang='hi')
        self.logger.info(f"Test large number: 'एक हजार दो सौ चौंतीस' -> {result}")
        self.assertEqual(result, 1234)

    def test_decimal_number(self):
        result = self.word_to_num.convert("एक दशमलव पांच", lang='hi')
        self.logger.info(f"Test decimal number: 'एक दशमलव पांच' -> {result}")
        self.assertEqual(result, 1.5)

    def test_mixed_number(self):
        result = self.word_to_num.convert("एक सौ तेईस दशमलव चार पांच छह", lang='hi')
        self.logger.info(f"Test mixed number: 'एक सौ तेईस दशमलव चार पांच छह' -> {result}")
        self.assertEqual(result, 123.456)

    def test_million_number(self):
        result = self.word_to_num.convert("दस लाख", lang='hi')
        self.logger.info(f"Test million number: 'दस लाख' -> {result}")
        self.assertEqual(result, 1000000)

    def test_invalid_word(self):
        with self.assertRaises(ValueError):
            self.word_to_num.convert("अमान्य", lang='hi')

    def test_shank(self):
        result = self.word_to_num.convert("एक शंख", lang='hi')
        self.logger.info(f"Test shank: 'एक शंख' -> {result}")
        self.assertEqual(result, 100000000000000000)

    def test_kharab(self):
        result = self.word_to_num.convert("एक खरब", lang='hi')
        self.logger.info(f"Test kharab: 'एक खरब' -> {result}")
        self.assertEqual(result, 100000000000)


class TestNumToWord(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/Hindi_test.log").get_logger()
        cls.logger.info("TestNumToWord started.")
        cls.num_to_word = NumberToWord()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestNumToWord completed. \n -----------------")

    def test_single_digit(self):
        result = self.num_to_word.convert(6, lang='hi')
        self.logger.info(f"Test single digit: 6 -> {result}")
        self.assertEqual(result, "छह")

    def test_two_digits(self):
        result = self.num_to_word.convert(21, lang='hi')
        self.logger.info(f"Test two digits: 21 -> {result}")
        self.assertEqual(result, "इक्कीस")

    def test_negative_number(self):
        result = self.num_to_word.convert(-1234, lang='hi')
        self.logger.info(f"Test negative number: -1234 -> {result}")
        self.assertEqual(result, "ऋणात्मक एक हजार दो सौ चौंतीस")

    def test_large_number(self):
        result = self.num_to_word.convert(1234, lang='hi')
        self.logger.info(f"Test large number: 1234 -> {result}")
        self.assertEqual(result, "एक हजार दो सौ चौंतीस")

    def test_decimal_number(self):
        result = self.num_to_word.convert(1.5, lang='hi')
        self.logger.info(f"Test decimal number: 1.5 -> {result}")
        self.assertEqual(result, "एक दशमलव पांच")

    def test_mixed_number(self):
        result = self.num_to_word.convert(123.456, lang='hi')
        self.logger.info(f"Test mixed number: 123.456 -> {result}")
        self.assertEqual(result, "एक सौ तेईस दशमलव चार पांच छह")

    def test_million_number(self):
        result = self.num_to_word.convert(1000000, lang='hi')
        self.logger.info(f"Test million number: 1000000 -> {result}")
        self.assertEqual(result, "दस लाख")


if __name__ == '__main__':
    unittest.main()
