from utility import GetLanguage


class WordToNumber:
    def __init__(self):
        self.word_to_num = None
        self.symbol = None

    def convert(self, words, lang="en"):
        """
        Convert a number in word form to its numerical representation.

        Args:
            words (str): The number in word form.
            lang (str): The language to use for the conversion.

        Returns:
            int | float: The numerical representation of the number.
        """
        self.__get_words(lang)
        words = self.__remove_helper_word(words.replace("-", " ").split(), lang)
        total, current, decimal_part, decimal_place = 0, 0, 0, 0.1
        is_decimal, is_negative = False, False

        for word in words:
            if word == self.symbol[1]:
                is_negative = True
            elif word == self.symbol[0]:
                is_decimal = True
            elif word.isdigit():
                current, decimal_part, decimal_place = self.process_digit(word, is_decimal, current, decimal_part,
                                                                          decimal_place)
            elif word in self.word_to_num:
                current, total, decimal_part, decimal_place = self.process_word(word, is_decimal, current, total,
                                                                                decimal_part, decimal_place)
            else:
                raise ValueError(f"Word '{word}' is not recognized.")

        result = total + current + decimal_part
        if is_negative:
            result = -result
        return result

    @staticmethod
    def process_digit(word, is_decimal, current, decimal_part, decimal_place):
        """
        Process a digit in the word form of a number.

        Args:
            word (str): The digit to process.
            is_decimal (bool): Whether the number is a decimal.
            current (int): The current value of the number.
            decimal_part (float): The decimal part of the number.
            decimal_place (float): The decimal place value.

        Returns:
            (int, float, float):
                - The updated current value.
                - The updated decimal part.
                - The updated decimal place value.
        """
        scale = int(word)
        if is_decimal:
            decimal_part += scale * decimal_place
            decimal_place /= 10
        else:
            current += scale
        return current, decimal_part, decimal_place

    def process_word(self, word, is_decimal, current, total, decimal_part, decimal_place):
        """
        Process a word in the word form of a number.

        Args:
            word (str): The word to process.
            is_decimal (bool): Whether the number is a decimal.
            current (int): The current value of the number.
            total (int): The total value of the number.
            decimal_part (float): The decimal part of the number.
            decimal_place (float): The decimal place value.

        Returns:
            (int, int, float, float):
                - The updated current value.
                - The updated total value.
                - The updated decimal part.
                - The updated decimal place value.
        """
        scale = self.word_to_num[word]
        if is_decimal:
            decimal_part += scale * decimal_place
            decimal_place /= 10
        else:
            current, total = self.update_total_and_current(scale, current, total)
        return current, total, decimal_part, decimal_place

    @staticmethod
    def update_total_and_current(scale, current, total):
        """
        Update the total and current values based on the scale.

        Args:
            scale (int): The scale of the word.
            current (int): The current value of the number.
            total (int): The total value of the number.

        Returns:
            (int, int):
                - The updated current value.
                - The updated total value.
        """
        if scale >= 1000:
            if current == 0:
                current = 1
            current *= scale
            total += current
            current = 0
        elif scale >= 100:
            if current == 0:
                current = 1
            current *= scale
        else:
            current += scale
        return current, total

    @staticmethod
    def __remove_helper_word(word_list, lang):
        helper_words = []
        if lang == 'fr':
            helper_words = ['et']
        return [word for word in word_list if word.lower() not in helper_words]

    def __get_words(self, lang):
        """
        Get the words for the number conversion based on the language.

        Args:
            lang (str): The language to use for the conversion.
        """
        self.word_to_num = GetLanguage().get_language(lang)[0]
        self.symbol = GetLanguage().get_language(lang)[2]
