from yta_general_utils.programming.enum import YTAEnum as Enum
from yta_validation.parameter import ParameterValidator
from requests import Response
from typing import Union

import json


class FileEncoding(Enum):
    """
    The different file encoding we accept. This Enum
    has been created to be used as encoding when
    writing on a file.

    # TODO: Maybe rename to 'TextEncoding'? Maybe use
    # an external library or move this to another
    # module (not library) (?)
    """

    UTF8 = 'utf8'

class FileWriter:
    """
    Class to simplify and encapsulate the functionality related with
    writting files.
    """

    @staticmethod
    def write_binary_file(
        binary_data: bytes,
        output_filename: str
    ) -> str:
        """
        Writes the provided 'binary_data' in the 'filename'
        file. It replaces the previous content if existing.

        This method returns the filename as written.
        """
        ParameterValidator.validate_mandatory('binary_data', binary_data)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        return _write_binary(
            binary_data,
            output_filename
        )

    @staticmethod
    def write_json_to_file(
        dict: dict,
        output_filename: str
    ) -> str:
        """
        Writes the provided 'dict' as a json into the 'filename'.

        This method returns the filename as written.

        @param
            **dict**
            Python dictionary that will be stored as a json.

            **output_filename**
            File path in which we are going to store the information.
        """
        ParameterValidator.validate_mandatory_dict('dict', dict)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        return FileWriter.write_file(
            text = json.dumps(dict, indent = 4),
            output_filename = output_filename
        )

    @staticmethod
    def write_file(
        text: str,
        output_filename: str,
        encoding: Union[str, FileEncoding, None] = FileEncoding.UTF8
    ) -> str:
        """
        Writes the provided 'text' in the 'filename' file. It
        replaces the previous content if existing.

        This method returns the filename that has been
        written.
        """
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = True)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        encoding = (
            None
            if encoding == None else
            FileEncoding.to_enum(encoding).value
        )

        return _write(text, encoding, output_filename)

    @staticmethod
    def write_file_by_chunks_from_response(
        response: Response,
        output_filename: str
    ) -> str:
        """
        Iterates over the provided 'response' and writes its content
        chunk by chunk in the also provided 'output_filename'.

        TODO: If you find a better way to handle this you are free to
        create new methods and move them into a new file.

        This method returns the filename that has been
        written.
        """
        ParameterValidator.validate_mandatory_instance_of('response', response, Response)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        CHUNK_SIZE = 32768

        # TODO: Make this method work with a common Iterator parameter
        # and not an specific response, please
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        return output_filename
    
def _write(
    content: str,
    encoding: Union[str, FileEncoding, None],
    output_filename: str
) -> str:
    """
    Returns the 'output_filename' that has been
    written.
    """
    encoding = (
        None
        if encoding == None else
        FileEncoding.to_enum(encoding).value
    )

    with open(
        file = output_filename,
        mode = 'w',
        encoding = encoding
    ) as f:
        f.write(content)

    return output_filename

def _write_binary(
    content: bytes,
    output_filename: str
) -> str:
    """
    Returns the 'output_filename' that has been
    written.
    """
    with open(
        file = output_filename,
        mode = 'wb'
    ) as f:
        f.write(content)

    return output_filename