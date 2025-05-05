from utility import GetLanguage


class HumanizeNumber:
    def __init__(self):
        self.suffixes = None

    def convert(self, number, lang='en', to_lang=None):
        if to_lang is not None:
            return self.__convert_to_lang(number, lang, to_lang)
        else:
            self.__get_word(lang)
            for value, suffix in self.suffixes:
                if number >= 10 ** value:
                    formatted_num = number / 10 ** value
                    if formatted_num.is_integer():
                        return f"{int(formatted_num)}{suffix}"
                    formatted_str = f"{formatted_num:.2f}"
                    if formatted_str[-1] == "0":
                        formatted_str = f"{formatted_num:.1f}"
                    return f"{formatted_str}{suffix}"

        return str(number)

    def __convert_to_lang(self, humanize_number, from_lang, to_lang):
        from_suffix = GetLanguage().get_language(from_lang)[3][::-1]

        for value, suffix in from_suffix:
            if suffix in humanize_number:
                number = float(humanize_number.replace(suffix, "")) * 10 ** value
                return self.convert(number, to_lang)

        return humanize_number

    def __get_word(self, lang='en'):
        self.suffixes = GetLanguage().get_language(lang)[3][::-1]
