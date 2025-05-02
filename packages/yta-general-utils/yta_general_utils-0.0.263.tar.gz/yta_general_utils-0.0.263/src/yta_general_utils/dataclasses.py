"""
When we handle files with our system we obtain them
in different formats. Sometimes we get them from urls
so they are just a bytes array, and sometimes we 
obtain an image, for example, that has been previously
loaded with its corresponding library.

We try to treat all those files in the same way so we
have created this class to interact with them and make
easier the way we handle them.
"""
from yta_general_utils.file.enums import FileTypeX
from yta_general_utils.file.reader import FileReader
from yta_validation import PythonValidator
from dataclasses import dataclass
from typing import Union

import io


@dataclass
class FileReturn:
    """
    This dataclass has been created to handle a file
    that has been created or downloaded, so we are
    able to return the file itself and also the 
    filename in the same return.
    """

    # TODO: Set valid types
    file: Union[bytes, bytearray, io.BytesIO, any]
    """
    The file content as raw as it was obtained by
    our system, that could be binary or maybe an
    actually parsed file.
    """
    type: Union[FileTypeX, None]
    """
    The type of the obtained file.
    """
    filename: str
    """
    The filename of the obtained file.
    """

    @property
    def file_type(self) -> Union[FileTypeX, None]:
        """
        Get the FileTypeX associated to the
        'output_filename' extension if existing and
        valid.
        """
        return FileTypeX.get_type_from_filename(self.filename)

    @property
    def file_converted(self):
        """
        The file parsed according to its type. This
        can be the same as 'file' attribute if it
        was obtained in a converted format.
        """
        # Sometimes the file that has been set is
        # already converted, so we just send it
        # as it is
        if not PythonValidator.is_instance(self.file, [bytes, bytearray, io.BytesIO]):
            return self.file
        
        if self.type is None:
            # TODO: What about this (?)
            import warnings
            warnings.warn('The type is None so we do not actually know the file type. Returning it raw.')
            return self.file

        return FileReader.parse_file_content(self.file, self.type)

    def __init__(
        self,
        file: Union[bytes, bytearray, io.BytesIO, any],
        type: Union[FileTypeX, None],
        filename: str
    ):
        if type is not None:
            type = FileTypeX.to_enum(type)

        self.file = file
        self.type = type
        self.filename = filename

