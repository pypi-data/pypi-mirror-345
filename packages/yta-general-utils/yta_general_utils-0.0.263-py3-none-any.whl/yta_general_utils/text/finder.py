from yta_general_utils.programming.enum import YTAEnum as Enum
from yta_general_utils.text.transformer import remove_marks_and_accents
from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass


@dataclass
class TermFound:
    """
    @dataclass
    A term found in a text, containing the indexes
    in which the term was found.
    """

    term: str
    """
    The term that has been found.
    """
    start_index: int
    """
    The index (within the text) in which the start
    of the 'term' has been found.
    """
    end_index: int
    """
    The index (within the text) in which the end
    of the 'term' has been found.
    """

    def __init__(
        self,
        term: str,
        start_index: int,
        end_index: int
    ) -> 'TermFound':
        ParameterValidator.validate_mandatory_string('term', term, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_int('start_index', start_index, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_int('end_index', end_index, do_include_zero = True)

        self.term = term
        self.start_index = start_index
        self.end_index = end_index


class TextFinderMode(Enum):
    """
    This is the mode in which we will look for the terms
    in the given segment text to find any coincidences.
    """

    EXACT = 'exact'
    """
    The term found must be exactly matched on the text,
    which means that accents and punctuation marks will
    be considered.
    """
    IGNORE_CASE_AND_ACCENTS = 'ignore_case_and_accents'
    """
    The term found must match, in lower case and ignoring
    the accents, the text.
    """

class TextFinder:
    """
    Class to simplify the way we look for texts
    within other texts.
    """

    @staticmethod
    def find_in_text(
        term: str,
        text: str,
        mode: TextFinderMode = TextFinderMode.IGNORE_CASE_AND_ACCENTS
    ) -> list[TermFound]:
        """
        Find the provided 'term' in the also provided
        'text' and obtain the start and end indexes
        of the 'term' according to that 'text'. The 
        term can be more than once in the 'text'.

        TODO: Add an ilustrative example.

        This method returns an array containing
        TermFound instances including the start and
        end indexes.
        """
        ParameterValidator.validate_mandatory_string('term', term, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = True)
        
        mode = TextFinderMode.to_enum(mode)

        if mode == TextFinderMode.IGNORE_CASE_AND_ACCENTS:
            term = remove_marks_and_accents(term).lower()
            text = remove_marks_and_accents(text).lower()

        text_words = text.split()
        term_words = term.split()
        
        # Store first and last index if found
        return [
            TermFound(
                term = term,
                start_index = i,
                end_index = i + len(term_words) - 1
            )
            for i in range(len(text_words) - len(term_words) + 1)
            if text_words[i:i + len(term_words)] == term_words
        ]