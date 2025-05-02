from yta_validation.number import NumberValidator

import random
import string


class Random:
    """
    Class to wrap our custom random methods.
    """

    @staticmethod
    def float_between(
        start: float,
        end: float,
        step: float
    ) -> float:
        """
        Get a random float number in between the range
        by the given 'start' and 'end' limits, using the
        also provided 'step'.

        The limits are inverted if the 'end' is lower
        than the 'start'.

        TODO: Is the limit included (?) Review and, if
        necessary, include it as a parameter.
        """
        if not NumberValidator.is_number(start):
            raise Exception('The provided "start" parameter is not a number.')
        
        if not NumberValidator.is_number(end):
            raise Exception('The provided "end" parameter is not a number.')
        
        if not NumberValidator.is_number(step):
            raise Exception('The provided "step" parameter is not a number.')
        
        start = float(start)
        end = float(end)
        step = float(step)

        # TODO: What about step = 0 or things like that (?)
        # TODO: What if 'start' and 'end' are the same (?)

        # Swap limits if needed
        start, end = end, start if end < start else start, end

        return random.choice([
            round(start + i * step, 4)
            for i in range(int((end - start) / step) + 1)
            if start + i * step <= end]
        )
    
    @staticmethod
    def int_between(
        start: int,
        end: int,
        step: int = 1 
    ) -> int:
        """
        Get a random int number in between the range
        by the given 'start' and 'end' limits, using the
        also provided 'step'.

        The limits are inverted if the 'end' is lower
        than the 'start'. The limist are included.
        """
        # TODO: What about strings that are actually parseable
        # as those numbers (?)
        if not NumberValidator.is_number(start):
            raise Exception('The provided "start" parameter is not a number.')
        
        if not NumberValidator.is_number(end):
            raise Exception('The provided "end" parameter is not a number.')
        
        if not NumberValidator.is_number(step):
            raise Exception('The provided "step" parameter is not a number.')
        
        start = int(start)
        end = int(end)
        step = int(step)

        # TODO: What about step = 0 or things like that (?)
        # TODO: What if 'start' and 'end' are the same (?)
        
        # Swap limits if needed
        start, end = end, start if end < start else start, end
        
        return random.randrange(start, end + 1, step)
    
    @staticmethod
    def bool():
        """
        Get a boolean value chosen randomly.
        """
        return bool(random.getrandbits(1))
    
    @staticmethod
    def characters(
        n: int = 10
    ):
        """
        Get a string with 'n' random characters.
        """
        return ''.join(random.choices(string.ascii_letters, k = n))
    
    @staticmethod
    def digits(
        n: int = 10
    ):
        """
        Get a string with 'n' random digits.
        """
        return ''.join(random.choices(string.digits, k = n))
    
    @staticmethod
    def characters_and_digits(
        n: int = 10
    ):
        """
        Get a string with 'n' random characters and digits.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k = n))