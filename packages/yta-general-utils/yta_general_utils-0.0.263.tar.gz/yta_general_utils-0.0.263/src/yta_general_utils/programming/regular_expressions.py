"""
When working with regular expressions, if we define
groups, that are part of regular expressions wrapped
with parenthesis, we can also obtain the part of the
input string that fits that group. If we don't, we
can only verify, in general, if the input string fits
the regular expression or not.
"""
from yta_general_utils.programming.enum import YTAEnum as Enum
from yta_validation.parameter import ParameterValidator
from yta_validation.number import NumberValidator
from typing import Union

import exrex
import re


class RegularExpression(Enum):
    """
    Enum class to represent a regular expression and
    simplify the way we work with them. Create a new
    YTAEnum class for your group of regular expressions
    inheriting from this class, declare your regular
    expressions with the expression as it value and
    you'll be able to use it.

    A regular expression can have or can have not
    groups, that are parts in the expression wrapped
    by parenthesis. These groups are used to look for
    those specific parts in the given string and are
    matched individually. The whole expression has to
    be found in the given string, but each group will
    detect its own hit.

    This is a regular expression with no groups:
    - r'@'

    This is a regular expression with 2 groups:
    - r'@([^:]+):([^@]+)@'
    """

    def __new__(
        cls,
        value: str
    ):
        # Force the enum to be a regular expression
        if not RegularExpression.is_valid_regex(value):
            raise Exception(f'The given value "{str(value)}" is not a regular expression.')
        
        obj = object.__new__(cls)
        obj._value_ = value

        return obj

    @property
    def compiled(
        self
    ) -> 'Pattern':
        """
        Get the regular expression but compiled.
        """
        if not hasattr(self, '_compiled'):
            self._compiled = re.compile(self.value)

        return self._compiled

    @property
    def has_groups(
        self
    ) -> bool:
        """
        Check if the expression has groups or not.
        """
        return self.number_of_groups > 0

    @property
    def number_of_groups(
        self
    ) -> int:
        """
        Get the number of groups that this regular expression
        has. A group is a part of the expression wrapped by
        parenthesis and it is used to detect that specific
        part of the expression in a given string.
        """
        return self.compiled.groups
    
    def parse(
        self,
        string: str
    ) -> bool:
        """
        @deprecated
        Check if the given 'string' is valid according to this
        regular expression.

        Use 'is_valid' function instead.
        """
        # TODO: Refactor code in any library and replace
        # 'parse' by 'is_valid'
        return self.is_valid(string)

    def is_valid(
        self,
        string: str
    ) -> bool:
        """
        Check if the given 'string' is valid according to this
        regular expression.
        """
        ParameterValidator.validate_mandatory_string('string', string, do_accept_empty = True)

        return bool(re.fullmatch(self.value, string))

    def find(
        self,
        string: str
    ) -> list[any]:
        """
        Find the coincidences of this regular expression within
        the given 'string'.

        If the regular expression doesn't contain groups, the
        result will be an array containing the different parts
        that have been hit by the regular expression. If it does
        contain groups, the result will be an array containing
        tuples. Each of those tuples position will contain each
        group hit.

        For example, for this text:
        - "example @param1:value1@"

        The regular expression r'@' will return:
        - ['@', '@']

        The regular expression r'@([^:]+):([^@]+)@' will return:
        - [('param1', 'value1')]
        """
        ParameterValidator.validate_mandatory_string('string', string, do_accept_empty = True)

        return re.findall(self.value, string)
    
    def get_matching_group(
        self,
        string: str,
        group_index: int
    ) -> Union[str, None]:
        """
        @deprecated
        Find the coincidences of this regular expression within
        the given 'string', but return only the 'group_index'
        group of the hit. If this regular expression has no
        groups this will return None.

        For example, for this text:
        - "example @param1:value1@"

        The regular expression r'@' will return:
        - None

        The regular expression r'@([^:]+):([^@]+)@' and the 1
        group index will return:
        - 'value1'

        Use 'find_group' function instead.
        """
        return self.find_group(string, group_index)

    def find_group(
        self,
        string: str,
        group_index: int
    ) -> Union[str, None]:
        """
        Find the coincidences of this regular expression within
        the given 'string', but return only the 'group_index'
        group of the hit. If this regular expression has no
        groups this will return None.

        For example, for this text:
        - "example @param1:value1@"

        The regular expression r'@' will return:
        - None

        The regular expression r'@([^:]+):([^@]+)@' and the 1
        group index will return:
        - 'value1'
        """
        if not self.has_groups:
            return None

        ParameterValidator.validate_mandatory_string('string', string, do_accept_empty = True)
        NumberValidator.is_number_between(group_index, 0, self.number_of_groups, do_include_upper_limit = False)

        matches = re.search(self.value, string)

        return (
            matches.group(group_index)
            if matches is not None else
            None
        )

    def generate(
        self,
    ) -> list[str]:
        """
        Generate a string that fits this regular expression.
        """
        return exrex.getone(self.value)
    
    @staticmethod
    def is_valid_regex(
        string: str
    ) -> bool:
        """
        Check if the provided 'string' is a valid regular
        expression or not, returning True or False.
        """
        try:
            re.compile(string)
            return True
        except re.error:
            return False
    
# TODO: Move this to more specific regular expressions and
# maybe hold them in the library you are using them
class GeneralRegularExpression(RegularExpression):
    """
    Enum class to encapsulate useful regular
    expressions for our system and to simplify
    the way we check those regular expressions
    with some provided parameters.
    """

    FILENAME_WITH_EXTENSION = r'^[\w,\s-]+\.[a-zA-Z0-9]{2,}$'
    """
    Check if the string is a filename with a valid extension (which must
    be a common filename with a dot '.' and at least two
    alphanumeric characters).
    
    Example of a valid input: 'filename.mp3'.
    """
    URL = r'^(http://|https://|file:///)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(/.*)?$'
    """
    Check if the string contains a valid url, that can
    start with one of these schemas ('http://', 'https://'
    or 'file:///') and continue with a valid url (domain,
    subdomain, etc.).
    """
    YOUTUBE_VIDEO_URL = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)(&.*)?$'
    """
    Check if the string contains a valid Youtube video url.

    Example of a valid input: 'https://www.youtube.com/watch?v=OpA2ZxnRs6'
    """
    TIKTOK_SHORT_VIDEO_URL = r'^https://vm\.tiktok\.com/[a-zA-Z0-9]+$'
    """
    Check if the string contains a valid Tiktok short video url.
    This url is generated when you share a Tiktok. (?)

    Example of a valid input:
    - 'https://vm.tiktok.com/ZGeSJ6YRA'
    """
    TIKTOK_LONG_VIDEO_URL = r'^https://www\.tiktok\.com/@[a-zA-Z0-9]+/video/\d+.*$'
    """
    Check if the string contains a valid Tiktok long video url.
    This url is the main url of a Tiktok video. (?)

    Example of a valid input:
    - 'https://www.tiktok.com/@ahorayasabesque/video/7327001175616703777?_t=8jqq93LWqsC&_r=1'
    """
    FACEBOOK_SHORT_REEL_URL = r'^https://www\.facebook\.com/share/r/[a-zA-Z0-9]+/?.*$'
    """
    Check if the string contains a valid Facebook reel
    short video url.

    Example of a valid input:
    - 'https://www.facebook.com/share/r/1ZBKSvZZVr/'
    """
    INSTAGRAM_SHORT_REEL_URL = r'^https://www\.instagram\.com/reel/[a-zA-Z0-9_-]+/?.*$'
    """
    Check if the string contains a valid Instagram reel
    short video url.

    Example of a valid input:
    - 'https://www.instagram.com/reel/DHQf6RmMFtf/?igsh=ZBDzeTA4cWkwbW4w''
    """
    SHORTCODE = r'\[(/?[a-zA-Z0-9-_]+)\]'
    """
    Check if the string is a valid opening or closing
    shortcode tag that can (the closing tag includes
    one slash '/' at the begining).
    """
    SNAKE_CASE = r'^[a-z0-9]+(?:_[a-z0-9]+)*$'
    """
    Check if the string is a valid snake case string.
    The snake case is something like 'this_is_snake'.
    """
    UPPER_CAMEL_CASE = r'^[A-Z][a-zA-Z0-9]*$'
    """
    Check if the string is a valid upper camel case
    string. The upper camel case string is something
    like 'ThisIsUpperCamelCase'.
    """
    LOWER_CAMEL_CASE = r'^[a-z][a-zA-Z0-9]*$'
    """
    Check if the string is a valid lower camel case
    string. The lower camel case string is something
    like 'ThisIsLowerCamelCase'.
    """