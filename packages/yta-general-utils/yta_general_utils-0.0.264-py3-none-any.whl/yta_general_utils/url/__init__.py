from yta_validation import PythonValidator
from urllib import parse as url_parse


# TODO: Refactor this
def encode_url_parameter(parameter: str):
    """
    Encode the provided 'parameter' to be able to send
    it throught as a url query parameter.

    This method will turn 'example message' to
    'example%20message'.
    """
    if not PythonValidator.is_string(parameter):
        raise Exception('The provided "parameter" parameter is not a string.')
    
    return url_parse.quote(parameter)

def encode_url_parameters(parameters: dict):
    """
    Encode the 'parameters' provided as a dict to be
    able to send them through a url query.

    This method will concatenate the parameters as
    '?query=esto%20es%20una%20frase&page=3...'.
    """
    if not PythonValidator.is_dict(parameters):
        raise Exception('The provided "parameters" parameter is not a dict.')
    
    return url_parse.urlencode(parameters)