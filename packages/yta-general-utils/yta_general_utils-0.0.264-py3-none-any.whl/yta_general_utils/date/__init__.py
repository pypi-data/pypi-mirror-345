from yta_validation.number import NumberValidator
from datetime import datetime


def get_rfc_datetime(year: int = 1900, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0):
    """
    Receives a date based on provided parameters and turns it into
    a RFC datetime, returning it.

    TODO: Explain this better, please
    """
    dt = datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'

    return dt

def seconds_to_hh_mm_ss(seconds: int):
    """
    Turn the provided amount of 'seconds' to a time
    in the format HH:MM:SS.
    """
    if not NumberValidator.is_positive_number(seconds, do_include_zero = True):
        raise Exception('The provided amount of "seconds" is not a positive number (including zero).')
    
    hh = seconds // 3600
    mm = (seconds % 3600) // 60 
    ss = seconds % 60

    return f'{hh:02}:{mm:02}:{ss:02}'

# TODO: Make this more configurable
def current_datetime() -> str:
    """
    Return the current time moment, as a string, in
    the 'DD/MM/YYYY HH:MM:SS' format.
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# TODO: Build more methods to simplify our work