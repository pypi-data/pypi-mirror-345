"""
TODO: This class has to be moved to another library as it
is using the ChromeScraper that is now in the
'yta_web_scraper' library.
"""
from yta_general_utils.web.scraper.chrome_scraper import google_translate
from yta_general_utils.constants import Language
from yta_validation.parameter import ParameterValidator


class GoogleTranslator:
    """
    Class to wrap the functionality that allows
    translating a text by using the Google Translator
    official web page with a web scrapper.
    """

    @staticmethod
    def translate(
        text: str,
        input: Language = Language.ENGLISH,
        output: Language = Language.SPANISH
    ) -> str:
        """
        Get the translation of the given 'text' from the
        provided 'input' language to the 'output' language.
        """
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        input = Language.to_enum(input)
        output = Language.to_enum(output)

        return google_translate(text, input.value, output.value)