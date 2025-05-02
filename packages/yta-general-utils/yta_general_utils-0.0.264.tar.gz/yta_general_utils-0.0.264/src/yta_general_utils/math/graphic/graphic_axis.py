from yta_validation.number import NumberValidator


class GraphicAxis:
    """
    Class that represent a Graphic axis with
    its min and max range.
    """

    range: tuple[float, float] = None
    """
    The range of the axis, a (min, max) tuple.
    """

    def __init__(self, min: float, max: float):
        if not NumberValidator.is_number(min) or not NumberValidator.is_number(max):
            raise Exception('The parameters "min" and "max" must be numbers.')
        
        if min >= max:
            raise Exception('The "min" parameter cannot be greater or equal than the "max" parameter.')

        self.range = (min, max)

    @property
    def min(self):
        """
        The minimum value.
        """
        return self.range[0]
    
    @property
    def max(self):
        """
        The maximum value.
        """
        return self.range[1]