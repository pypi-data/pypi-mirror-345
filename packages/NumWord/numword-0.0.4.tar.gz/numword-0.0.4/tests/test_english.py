import unittest

from Logs import LoggerConfig
from NumWord import WordToNumber, NumberToWord


class TestWordToNum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/English_test.log").get_logger()
        cls.logger.info("TestWordToNum started.")
        cls.word_to_num = WordToNumber()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestWordToNum completed. \n -----------------")

    def test_single_digit(self):
        result = self.word_to_num.convert("five")
        self.logger.info(f"Test single digit: 'five' -> {result}")
        self.assertEqual(result, 5)

    def test_two_digits(self):
        result = self.word_to_num.convert("twenty-one")
        self.logger.info(f"Test two digits: 'twenty-one' -> {result}")
        self.assertEqual(result, 21)

    def test_negative_number(self):
        result = self.word_to_num.convert("negative one thousand two hundred thirty-four")
        self.logger.info(f"Test negative number: 'negative one thousand two hundred thirty-four' -> {result}")
        self.assertEqual(result, -1234)

    def test_large_number(self):
        result = self.word_to_num.convert("one thousand two hundred thirty-four")
        self.logger.info(f"Test large number: 'one thousand two hundred thirty-four' -> {result}")
        self.assertEqual(result, 1234)

    def test_decimal_number(self):
        result = self.word_to_num.convert("one point five")
        self.logger.info(f"Test decimal number: 'one point five' -> {result}")
        self.assertEqual(result, 1.5)

    def test_mixed_number(self):
        result = self.word_to_num.convert("one hundred twenty-three point four five six")
        self.logger.info(f"Test mixed number: 'one hundred twenty three point four five six' -> {result}")
        self.assertEqual(result, 123.456)

    def test_million_number(self):
        result = self.word_to_num.convert("one million two hundred thirty-four thousand five hundred sixty-seven")
        self.logger.info(
            f"Test million number: 'one million two hundred thirty-four thousand five hundred sixty-seven' -> {result}")
        self.assertEqual(result, 1234567)

    def test_trillion_number(self):
        result = self.word_to_num.convert(
            "one trillion two hundred thirty-four billion five hundred sixty-seven million eight hundred ninety thousand one hundred twenty-three")
        self.logger.info(
            f"Test trillion number: 'one trillion two hundred thirty-four billion five hundred sixty-seven million eight hundred ninety thousand one hundred twenty-three' -> {result}")
        self.assertEqual(result, 1234567890123)

    def test_quintillion_number(self):
        result = self.word_to_num.convert(
            "one quintillion two hundred thirty-four quadrillion five hundred sixty-seven trillion eight hundred ninety billion one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine")
        self.logger.info(
            f"Test quintillion number: 'one quintillion two hundred thirty-four quadrillion five hundred sixty-seven trillion eight-hundred ninety billion one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine' -> {result}")
        self.assertEqual(result, 1234567890123456789)

    def test_invalid_word(self):
        with self.assertRaises(ValueError):
            self.word_to_num.convert("invalid")

    def test_number_in_words(self):
        result = self.word_to_num.convert("one hundred 23 point four five six")
        self.logger.info(f"Test number in words: 'one hundred 23 point four five six' -> {result}")
        self.assertEqual(result, 123.456)

    def test_decimal_digit(self):
        result = self.word_to_num.convert("one point 0 five")
        self.logger.info(f"Test decimal digit: 'one point 0 five' -> {result}")
        self.assertEqual(result, 1.05)


class TestNumToWord(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerConfig(__name__, file_name="TestLogs/English_test.log").get_logger()
        cls.logger.info("TestNumToWord started.")
        cls.num_to_word = NumberToWord()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestNumToWord completed. \n -----------------")

    def test_single_digit(self):
        result = self.num_to_word.convert(5)
        self.logger.info(f"Test single digit: 5 -> {result}")
        self.assertEqual(result, "five")

    def test_two_digits(self):
        result = self.num_to_word.convert(21)
        self.logger.info(f"Test two digits: 21 -> {result}")
        self.assertEqual(result, "twenty-one")

    def test_teen_number(self):
        result = self.num_to_word.convert(15)
        self.logger.info(f"Test teen number: 15 -> {result}")
        self.assertEqual(result, "fifteen")

    def test_ten_number(self):
        result = self.num_to_word.convert(10)
        self.logger.info(f"Test ten number: 10 -> {result}")
        self.assertEqual(result, "ten")

    def test_zero_number(self):
        result = self.num_to_word.convert(0)
        self.logger.info(f"Test zero number: 0 -> {result}")
        self.assertEqual(result, "zero")

    def test_hundred_number(self):
        result = self.num_to_word.convert(115)
        self.logger.info(f"Test hundred number: 115 -> {result}")
        self.assertEqual(result, "one hundred fifteen")

    def test_large_number(self):
        result = self.num_to_word.convert(1234)
        self.logger.info(f"Test large number: 1234 -> {result}")
        self.assertEqual(result, "one thousand two hundred thirty-four")

    def test_negative_number(self):
        result = self.num_to_word.convert(-1234)
        self.logger.info(f"Test negative number: -1234 -> {result}")
        self.assertEqual(result, "negative one thousand two hundred thirty-four")

    def test_decimal_number(self):
        result = self.num_to_word.convert(1.5)
        self.logger.info(f"Test decimal number: 1.5 -> {result}")
        self.assertEqual(result, "one point five")

    def test_mixed_number(self):
        result = self.num_to_word.convert(123.456)
        self.logger.info(f"Test mixed number: 123.456 -> {result}")
        self.assertEqual(result, "one hundred twenty-three point four five six")

    def test_million_number(self):
        result = self.num_to_word.convert(1234567)
        self.logger.info(f"Test million number: 1234567 -> {result}")
        self.assertEqual(result, "one million two hundred thirty-four thousand five hundred sixty-seven")

    def test_trillion_number(self):
        result = self.num_to_word.convert(1234567890123)
        self.logger.info(f"Test trillion number: 1234567890123 -> {result}")
        self.assertEqual(result,
                         "one trillion two hundred thirty-four billion five hundred sixty-seven million eight hundred ninety thousand one hundred twenty-three")

    def test_quintillion_number(self):
        result = self.num_to_word.convert(1234567890123456789)
        self.logger.info(f"Test quintillion number: 1234567890123456789 -> {result}")
        self.assertEqual(result,
                         "one quintillion two hundred thirty-four quadrillion five hundred sixty-seven trillion eight hundred ninety billion one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine")

    def test_hundred_then_thousand(self):
        result = self.num_to_word.convert(105000)
        self.logger.info(f"Test hundred then thousand: 105000 -> {result}")
        self.assertEqual(result, "one hundred five thousand")

    def test_more_then_nonillion(self):
        result = self.num_to_word.convert(10 ** 30)
        self.logger.info(f"Test more than nonillion: {10 ** 30} -> {result}")
        self.assertEqual(result, "one nonillion")


if __name__ == '__main__':
    unittest.main()
