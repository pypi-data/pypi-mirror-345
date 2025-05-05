from utility import GetLanguage


class NumberToWord:
    def __init__(self):
        self.symbol = None
        self.thousands = None
        self.tens = None
        self.others = None
        self.teens = None
        self.units = None

    def convert_hundreds(self, number, lang):
        """
        Convert a number in the hundreds range to its word representation.

        Args:
            number (int): The number to convert.
            lang (str): The language to use for the conversion

        Returns:
            str: The word representation of the number.
        """
        if number > 99:
            return self.units[number // 100] + f" {self.zero[1]} " + self.convert_tens(number % 100, lang)
        else:
            return self.convert_tens(number, lang)

    def convert_tens(self, number, lang):
        """
        Convert a number in the tens range to its word representation.

        Args:
            number (int): The number to convert.
            lang (str): The language to use for the conversion

        Returns:
            str: The word representation of the number.
        """
        if lang == "fr":
            if 71 <= number <= 79:
                return f"{self.convert_tens(60, lang)}-{self.convert_tens(number - 60, lang)}"
            elif 91 <= number <= 99:
                return f"{self.convert_tens(80, lang)}-{self.convert_tens(number - 80, lang)}"
        if number < 10:
            return self.units[number]
        elif 10 < number < 20:
            return self.teens[number - 10]
        elif lang in ["hi"] and 20 <= number < 100:
            return self.others[number - 10]
        else:
            if number % 10 == 0:
                return self.tens[number // 10]
            return f"{self.tens[number // 10]}{self.__add_helper_word(number, lang)}{self.units[number % 10]}"

    @staticmethod
    def __add_helper_word(number, lang):
        if lang == "fr" and number % 10 == 1 and number not in [81, 91]:
            return "-et-"
        else:
            return "-"

    def convert_thousands(self, number, lang):
        """
        Convert a number in the thousands range to its word representation.

        Args:
            number (int): The number to convert.
            lang (str): The language to use for the conversion

        Returns:
            str: The word representation of the number.
        """
        if number == 0:
            return ""
        elif number < 1000:
            return self.convert_hundreds(number, lang).strip()
        else:
            for idx, word in enumerate(self.thousands):
                divisor = 10 ** self.power[idx]
                if number >= divisor:
                    return (self.convert_thousands(number // divisor, lang) + f" {self.thousands[idx]} " +
                            self.convert_thousands(number % divisor, lang).strip())

    def convert_decimal(self, number):
        """
        Convert the decimal part of a number to its word representation.

        Args:
            number (float): The number to convert.

        Returns:
            str: The word representation of the decimal part of the number.
        """
        decimal_part = str(number).split(".")[1]
        decimal_words = " ".join(self.units[int(digit)] for digit in decimal_part)
        return f"{self.symbol[0]} " + decimal_words

    def convert(self, number, lang="en"):
        """
        Convert a number to its word representation.

        Args:
            number (int or float): The number to convert.
            lang (str): The language to use for the conversion

        Returns:
            str: The word representation of the number.
        """
        self.__get_words(lang)
        if number == 0:
            return self.zero[0]
        elif number < 0:
            return f"{self.symbol[1]} " + self.convert(-number, lang)
        else:
            if "." in str(number):
                integer_part = int(str(number).split(".")[0])
                return self.convert_thousands(integer_part, lang).strip() + " " + self.convert_decimal(number)
            else:
                return self.convert_thousands(number, lang).strip()

    def __get_words(self, lang):
        """
        Get the words for the number conversion based on the language.

        Args:
            lang (str): The language to use for the conversion
        """
        self.zero = GetLanguage().get_language(lang)[1]["ZERO"]
        self.units = GetLanguage().get_language(lang)[1]["UNIT"]
        self.teens = GetLanguage().get_language(lang)[1]["TEENS"]
        self.others = GetLanguage().get_language(lang)[1]["OTHERS"]
        self.tens = GetLanguage().get_language(lang)[1]["TENS"]
        self.thousands = GetLanguage().get_language(lang)[1]["THOUSANDS"][::-1]
        self.symbol = GetLanguage().get_language(lang)[2]
        self.power = GetLanguage().get_language(lang)[1]["POWER"][::-1]
