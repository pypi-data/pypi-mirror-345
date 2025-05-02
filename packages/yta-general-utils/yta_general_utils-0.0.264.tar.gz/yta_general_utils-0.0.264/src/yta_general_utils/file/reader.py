from yta_general_utils.file.checker import FileValidator
from yta_general_utils.file.enums import FileTypeX
from yta_validation import PythonValidator
from moviepy import VideoFileClip
from pydub import AudioSegment
from PIL import Image
from typing import Union

import json
import io


class FileReader:
    """
    Class to simplify and encapsulate the functionality related
    with reading files.
    """

    @staticmethod
    def read_json(
        filename: str
    ):
        """
        Reads the provided 'filename' and returns the information 
        as a json (if possible).

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        if not PythonValidator.is_string(filename) or not FileValidator.file_exists(filename):
            raise Exception('The provided "filename" is not a valid string or filename.')
        
        with open(filename, encoding = 'utf-8') as json_file:
            return json.load(json_file)
        
    @staticmethod
    def read_lines(
        filename: str
    ):
        """
        Read the content of the provided 'filename'
        if valid and return it as it decomposed in
        lines.

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        if not PythonValidator.is_string(filename) or not FileValidator.file_exists(filename):
            raise Exception('The provided "filename" is not a valid string or filename.')
        
        with open(filename, 'r', encoding = 'utf-8') as file:
            return file.readlines()
        
    @staticmethod
    def read(
        filename: str
    ):
        """
        Read the content of the provided 'filename'
        if valid and return it as it is.

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        if not PythonValidator.is_string(filename) or not FileValidator.file_exists(filename):
            raise Exception('The provided "filename" is not a valid string or filename.')
        
        with open(filename, 'r', encoding = 'utf-8') as file:
            return file.read()

    @staticmethod
    def parse_file_content(
        file_content: Union[bytes, bytearray, io.BytesIO],
        file_type: FileTypeX
    ) -> Union[VideoFileClip, str, AudioSegment, Image.Image]:
        """
        Parse the provided 'file_content' with the given
        'file_type' and return that content able to be
        handled.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        if not PythonValidator.is_instance(file_content, [bytes, bytearray, io.BytesIO]):
            raise Exception('The provided "file_content" parameter is not bytes or bytearray.')
        
        file_type = FileTypeX.to_enum(file_type)
        
        if PythonValidator.is_instance(file_content, [bytes, bytearray]):
            # If bytes, load as a file in memory
            file_content = io.BytesIO(file_content)

        parse_fn = {
            FileTypeX.VIDEO: lambda file_content: VideoFileClip(file_content),
            FileTypeX.SUBTITLE: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileTypeX.TEXT: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileTypeX.AUDIO: lambda file_content: AudioSegment.from_file(file_content),
            FileTypeX.IMAGE: lambda file_content: Image.open(file_content)
        }.get(file_type, None)

        return parse_fn(file_content) if parse_fn else None

    @staticmethod
    def parse_filename(
        filename: str,
    ) -> Union[VideoFileClip, str, AudioSegment, Image.Image]:
        """
        Identify the provided 'filename' extension and open
        it according to the detected file type.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        reader_fn = {
            FileTypeX.VIDEO: lambda filename: VideoFileClip(filename),
            FileTypeX.SUBTITLE: lambda filename: FileReader.read(filename),
            FileTypeX.TEXT: lambda filename: FileReader.read(filename),
            FileTypeX.AUDIO: lambda filename: AudioSegment.from_file(filename),
            FileTypeX.IMAGE: lambda filename: Image.open(filename)
        }.get(FileTypeX.get_type_from_filename(filename), None)

        return reader_fn(filename) if reader_fn else None