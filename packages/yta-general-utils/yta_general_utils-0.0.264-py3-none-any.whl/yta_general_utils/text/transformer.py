from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from typing import Union

import unicodedata
import re


# TODO: Maybe wrap all this in a StringHandler class or similar
def remove_accents(
    text: str
) -> str:
    """
    Get the provided 'text' with the accents removed.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')

    return ''.join(
        char
        for char in unicodedata.normalize('NFD', text)
        if unicodedata.category(char) != 'Mn'
    )

def remove_marks(
    text: str
) -> str:
    """
    Get the provided 'text' without any quotation mark, parenthesis,
    full stops, commas, etc.
    
    Marks that are being removed:
    - '?', '¿', ',', '.', '¡', '!', '(', ')'

    TODO: This below could work eliminating no white spaces.
    pattern = re.compile('[\W_]+')
    return pattern.sub('', s)
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    # TODO: Try with a 're' implementation maybe (?)
    MARKS_TO_REMOVE = ['?', '¿', ',', '.', '¡', '!', '(', ')']

    for mark in MARKS_TO_REMOVE:
        text = text.replace(mark, '')

    return text

def remove_marks_and_accents(
    text: str
) -> str:
    """
    Get the provided 'text' without accents and marks.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    return remove_accents(remove_marks(text))

def remove_non_ascii_characters(
    text: str,
    do_remove_accents: bool = True
) -> str:
    """
    Removes any non-ascii character from the provided 'text' and returns it
    modified.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    s = (
        list(remove_accents(text))
        if do_remove_accents else
        list(text)
    )
    index = 0
    while index < len(s):
        char = s[index]
        if not char.isascii():
            del s[index]
        else:
            index += 1

    return ''.join(s)

def fix_ellipsis(
    text: str
) -> str:
    """
    This method fixes the provided 'text' by removing the
    existing ellipsis (...).
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    text = re.sub(r'\.\.\.+', '', text)

    return text

def fix_unseparated_periods(
    text: str
) -> str:
    """
    This method fixes the provided 'text' by applying a space
    after any period without it.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    # Thank you: https://stackoverflow.com/a/70394076
    text = re.sub(r'\.(?!(?<=\d\.)\d) ?', '. ', text)
    
    return text

def fix_separated_parenthesis(
    text: str
) -> str:
    """
    This method remove the spaces that are found before or/and
    after any parenthesis. For example, '( esto es de prueba )'
    will become '(esto es de prueba)'.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    def fix_match(match):
        opening, content, closure = match.groups()
        if content:
            # Remove the whitespaces
            without_whitespaces = re.sub(r'\s+', ' ', content.strip())
            return f'{opening}{without_whitespaces}{closure}'
        
        return match.group(0)
    
    text = re.sub(r'(\()([^\(\)]+?)(\))', fix_match, text)
    
    return text

def fix_separated_square_brackets(
    text: str
) -> str:
    """
    This method removes the spaces that are found before or/and
    after any square bracket. For example, '[  shortcode ]' will
    become '[shortcode]'
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    def fix_match(match):
        opening, content, closure = match.groups()
        if content:
            # Remove the whitespaces
            without_whitespaces = re.sub(r'\s+', ' ', content.strip())
            return f'{opening}{without_whitespaces}{closure}'
        
        return match.group(0)
    
    text = re.sub(r'(\[)([^\[\]]+?)(\])', fix_match, text)
    
    return text

def add_missing_spaces_before_and_after_parenthesis(
    text: str
) -> str:
    """
    This method adds the missing spaces before and after any 
    parenthesis in the provided 'text'. For example, 'hola(nueve)siete'
    will become 'hola (nueve) siete'.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    text = re.sub(r'(?<!\s)\((?!\s)', ' (', text)
    text = re.sub(r'\)(?!\s)', ') ', text)
    
    return text

def add_missing_spaces_before_and_after_square_brackets(
    text: str
) -> str:
    """
    This method adds the missing spaces before and after any 
    square bracket in the provided 'text'. For example, 
    'hola[nueve]siete' will become 'hola [nueve] siete'.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    text = re.sub(r'(?<!\s)\[(?!\s)', ' [', text)
    text = re.sub(r'\](?!\s)', '] ', text)
    
    return text

def fix_excesive_blank_spaces(
    text: str
) -> str:
    """
    Checks the provided 'text' and removes the extra blank spaces.
    This means that any sentence with more than one blank space 
    will be replaced by only one blank space.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    # TODO: Is this better (?)
    return re.sub(r'\s+', ' ', text)
    
    # TODO: Ok, why am I using not the 'repl' param in re.search?
    # I'm applying it in the new method below, please check if
    # valid to avoid the while, thank you
    filtered = re.search('[ ]{2,}', text)
    while filtered:
        index_to_replace = filtered.end() - 1
        s = list(text)
        s[index_to_replace] = ''
        text = ''.join(s)
        filtered = re.search('[ ]{2,}', text)

    return text

def strip(
    text: str
) -> str:
    """
    An enhanced version of the python's '.strip()' method
    that only allows one blank space, removing any 
    consecutive blank spaces group (even in the middle of
    a sentence). Of course, this method will remove any
    blank space at the begining or at the end of the 
    provided 'text' as the original '.strip()' method would
    do.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    return fix_excesive_blank_spaces(text).strip()

def numbers_to_text(
    text: str
) -> str:
    """
    This method receives a text that could contain numbers
    and turns those numbers into text, which is useful to
    let narration software work with just text and avoid
    numbers problems.

    This method gives the result in Spanish language.
    """
    if not PythonValidator.is_string(text):
        raise Exception('The provided "text" parameter is not a string.')
    
    words = str(text).split(' ')

    SPECIAL_CHARS = ['¡', '!', ',', '.', '¿', '?', ':', '"', '\'', '#', '@']
    new_words = []
    # Iterate over each word to turn numbers into words
    for word in words:
        begining = ''
        ending = ''

        # We need to remove special chars at the begining or at the ending
        # to be able to work well with the important part of the word, but
        # we cannot simply delete ',' or '.' because could be in the middle
        # of a word
        if word[0] in SPECIAL_CHARS:
            begining = word[0]
            word = word[1:]
        if word[len(word) - 1] in SPECIAL_CHARS:
            ending = word[len(word) - 1]
            word = word[:1]

        try:
            word = float(word)
            # If here, it is a number, lets change its name
            # TODO: Implement logic here, so word will be the text, not the number
            print('Processing number: ' + str(word))
            accumulated_text = ''
            # We receive 123.456.789
            is_million = False
            is_one = False
            is_thousand = False
            is_ten = False
            divisor = 1_000_000_000
            res = int(word / divisor)  # 1 . 000 . 000 . 000
            if res >= 1:
                is_million = True
                is_thousand = True
                accumulated_text += __process_unit(res)
                word -= divisor * res

            if is_thousand:
                accumulated_text += ' mil'
                is_thousand = False

            divisor = 100_000_000
            res = int(word / divisor)  # 100 . 000 . 000
            if res >= 1:
                is_million = True
                if res == 1:
                    is_one = True
                accumulated_text += __process_hundred(res)
                word -= divisor * res

            divisor = 10_000_000
            res = int(word / divisor) # 10 . 000 . 000
            if res >= 1:
                is_million = True
                is_ten = True
                if is_one:
                    accumulated_text += 'to'
                    is_one = False
                accumulated_text += __process_ten(res)
                word -= divisor * res

            divisor = 1_000_000
            res = int(word / divisor) # 1 . 000 . 000
            if res >= 1:
                is_million = True
                if is_one:
                    accumulated_text += 'to'
                    is_one: False
                if is_ten:
                    accumulated_text += ' y '
                    is_ten = False
                accumulated_text += __process_unit(res)
                word -= divisor * res

            if is_million:
                accumulated_text += ' millones'
                is_million = False

            divisor = 100_000
            res = int(word / divisor) # 100 . 000
            if res >= 1:
                is_thousand = True
                if res == 1:
                    is_one = True
                accumulated_text += __process_hundred(res)
                word -= divisor * res

            divisor = 10_000
            res = int(word / divisor) # 10 . 000
            if res >= 1:
                is_thousand = True
                is_ten = True
                if is_one:
                    accumulated_text += 'to'
                    is_one = False
                accumulated_text += __process_ten(res)
                word -= divisor * res

            divisor = 1_000
            res = int(word / divisor) # 1 . 000
            if res >= 1:
                is_thousand = True
                if is_one:
                    accumulated_text += 'to'
                    is_one = False
                if is_ten:
                    accumulated_text += ' y '
                    is_ten = False
                accumulated_text += __process_unit(res)
                word -= divisor * res

            if is_thousand:
                accumulated_text += ' mil'
                is_thousand = False

            divisor = 100
            res = int(word / divisor) # 100
            if res >= 1:
                is_thousand = True
                if res == 1:
                    is_one = True
                accumulated_text += __process_hundred(res)
                word -= divisor * res

            divisor = 10
            res = int(word / divisor) # 10
            if res >= 1:
                is_thousand = True
                is_ten = True
                if is_one:
                    accumulated_text += 'to'
                    is_one = False
                accumulated_text += __process_ten(res)
                word -= divisor * res

            divisor = 1
            res = int(word / divisor) # 1
            if res >= 1:
                is_thousand = True
                if is_one:
                    accumulated_text += 'to'
                    is_one = False
                if is_ten:
                    accumulated_text += ' y '
                    is_ten = False
                accumulated_text += __process_unit(res)
                word -= divisor * res

            accumulated_text = accumulated_text.replace('  ', ' ').strip()
            # We need to replace in special cases
            accumulated_text = accumulated_text.replace('veinte y nueve', 'veintinueve')
            accumulated_text = accumulated_text.replace('veinte y ocho', 'veintiocho')
            accumulated_text = accumulated_text.replace('veinte y siete', 'veintisiete')
            accumulated_text = accumulated_text.replace('veinte y seis', 'veintiséis')
            accumulated_text = accumulated_text.replace('veinte y cinco', 'veinticinco')
            accumulated_text = accumulated_text.replace('veinte y cuatro', 'veinticuatro')
            accumulated_text = accumulated_text.replace('veinte y tres', 'veintitrés')
            accumulated_text = accumulated_text.replace('veinte y dos', 'veintidós')
            accumulated_text = accumulated_text.replace('veinte y uno', 'veintiuno')
            accumulated_text = accumulated_text.replace('diez y nueve', 'diecinueve')
            accumulated_text = accumulated_text.replace('diez y ocho', 'dieciocho')
            accumulated_text = accumulated_text.replace('diez y siete', 'diecisiete')
            accumulated_text = accumulated_text.replace('diez y seis', 'dieciséis')
            accumulated_text = accumulated_text.replace('diez y cinco', 'quince')
            accumulated_text = accumulated_text.replace('diez y cuatro', 'catorce')
            accumulated_text = accumulated_text.replace('diez y tres', 'trece')
            accumulated_text = accumulated_text.replace('diez y dos', 'doce')
            accumulated_text = accumulated_text.replace('diez y uno', 'once')

            word = accumulated_text
        except:
            pass

        new_words.append(begining + str(word) + ending)

    # We have the same size in 'words' and 'new_words', so lets build it
    final_text = " ".join(new_words)
    
    return final_text


def __process_hundred(
    number: Union[int, float]
) -> str:
    """
    Receives a digit that represente the X00 part of a number and returns
    that number (according to its position) in words.

    This method returns ' novecientos' for 9 input and ' cien' for 1 input.
    """
    if not NumberValidator.is_number(number):
        raise Exception('The provided "number" parameter is not a number.')
    
    number = {
        9: 'novecientos',
        8: 'ochocientos',
        7: 'setecientos',
        6: 'seiscientos',
        5: 'quinientos',
        4: 'cuatrocientos',
        3: 'trescientos',
        2: 'doscientos',
        1: 'cien'
    }[abs(number)]

    return f' {number}'

def __process_ten(
    number: Union[int, float]
) -> str:
    """
    Receives a digit that represente the X0 part of a number and returns
    that number (according to its position) in words.

    This method returns ' noventa' for 9 input and ' diez' for 1 input.
    """
    if not NumberValidator.is_number(number):
        raise Exception('The provided "number" parameter is not a number.')
    
    number = {
        9: 'noventa',
        8: 'ochenta',
        7: 'setenta',
        6: 'sesenta',
        5: 'cincuenta',
        4: 'cuarenta',
        3: 'treinta',
        2: 'veinte',
        1: 'diez'
    }[abs(number)]

    return f' {number}'

def __process_unit(
    number: Union[int, float]
) -> str:
    """
    Receives a digit that represente the X part of a number and returns
    that number (according to its position) in words.

    This method returns ' nueve' for 9 input, and ' uno' for 1 input.
    """
    if not NumberValidator.is_number(number):
        raise Exception('The provided "number" parameter is not a number.')
    
    number = {
        9: 'nueve',
        8: 'ocho',
        7: 'siete',
        6: 'seis',
        5: 'cinco',
        4: 'cuatro',
        3: 'tres',
        2: 'dos',
        1: 'uno'
    }[abs(number)]

    return f' {number}'