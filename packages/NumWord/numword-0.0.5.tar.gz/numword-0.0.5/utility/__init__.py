from .english import ENGLISH_NUM_WORDS, ENGLISH_WORD_NUM
from .french import FRENCH_WORD_NUM, FRENCH_NUM_WORDS
# from .german import GERMAN_WORD_NUM, GERMAN_NUM_WORDS
from .hindi import HINDI_NUM_WORDS, HINDI_WORD_NUM

from .symboles import SYMBOLS, SUFFIXES


class GetLanguage:
    def get_language(self, language):
        if language == "en":
            return ENGLISH_WORD_NUM, ENGLISH_NUM_WORDS, SYMBOLS["en"], SUFFIXES["en"]
        elif language == "hi":
            return HINDI_WORD_NUM, HINDI_NUM_WORDS, SYMBOLS["hi"], SUFFIXES["hi"]
        elif language == "en-hi":
            return ENGLISH_WORD_NUM, HINDI_NUM_WORDS, SYMBOLS["en"], SUFFIXES["en-hi"]
        elif language == "fr":
            return  FRENCH_WORD_NUM, FRENCH_NUM_WORDS, SYMBOLS["fr"], SUFFIXES["fr"]
        # elif language == "de":
        #     return GERMAN_WORD_NUM, GERMAN_NUM_WORDS, SYMBOLS["de"], SUFFIXES["de"]
        else:
            raise NotImplementedError(f"Language {language} is not supported.")
