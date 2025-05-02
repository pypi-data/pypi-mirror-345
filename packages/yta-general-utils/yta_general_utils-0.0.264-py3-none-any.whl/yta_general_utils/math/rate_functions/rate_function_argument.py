from yta_general_utils.math.rate_functions.rate_function import RateFunction
from yta_validation import PythonValidator
from typing import Union


class RateFunctionArgument:
    """
    An argument that can act as a rate function
    modifying the calculations for the animations
    we need. Anything that is able to recalculate
    an 'n' normalized value according and return
    it is accepted here.

    Check the accepted types in the '__init__'
    method.
    """

    def __init__(
        self,
        argument: Union['RateFunction', 'RateFunctionGraphic']
    ):
        if not PythonValidator.is_instance(argument, ['RateFunction', 'RateFunctionGraphic']):
            raise Exception('The provided "argument" parameter is not an instance of RateFunction nor RateFunctionGraphic class.')
        
        self.argument = argument
    
    def get_n_value(
        self,
        n: float
    ):
        """
        Get the corresponding value for the given 'n' normalized
        value that must be between 0 and 1.
        """
        return self.argument.get_n_value(n)
    
    @staticmethod
    def default():
        """
        Return a default instance of this class, perfect to
        be used as a parameter default value.
        """
        return RateFunctionArgument(RateFunction.LINEAR)