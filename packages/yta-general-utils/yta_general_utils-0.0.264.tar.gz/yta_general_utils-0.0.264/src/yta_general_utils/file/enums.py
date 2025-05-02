from yta_general_utils.programming.enum import YTAEnum as Enum
from yta_general_utils.temp import Temp
from yta_general_utils.random import Random
from yta_validation import PythonValidator
from typing import Union

import os


class FileExtension(Enum):
    """
    Enum class to encapsulate all the file
    extensions that we are able to handle.
    """

    # IMAGE
    PNG = 'png'
    """
    Portable Network Graphics
    """
    JPEG = 'jpeg'
    """
    Joint Photographic Experts Group
    """
    JPG = 'jpg'
    """
    Joint Photographic Experts Group
    """
    WEBP = 'webp'
    """
    Web Picture
    """
    BMP = 'bmp'
    """
    Bitmap Image File
    """
    GIF = 'gif'
    """
    Graphics Interchange Format
    """
    TIFF = 'tiff'
    """
    Tagged Image File
    """
    PSD = 'psd'
    """
    Photoshop Document
    """
    PDF = 'pdf'
    """
    Portable Document Format
    """
    DOC = 'doc'
    """
    Microsoft Word document old format.
    """
    DOCX = 'docx'
    """
    Microsoft Word document new format.
    """
    EPS = 'eps'
    """
    Encapsulated Postcript
    """
    AI = 'ai'
    """
    Adobe ILlustrator Document
    """
    INDD = 'indd'
    """
    Adobe Indesign Document
    """
    RAW = 'raw'
    """
    Raw Image Formats
    """
    CDR = 'cdr'
    """
    Corel Draw
    """
    # AUDIO
    WAV = 'wav'
    """
    Waveform Audio
    """
    MP3 = 'mp3'
    """
    MPEG Audio Layer 3.
    """
    M4A = 'm4a'
    """
    MPEG-4 Audio
    """
    FLAC = 'flac'
    """
    Free Lossless Audio Codec.
    """
    WMA = 'wma'
    """
    Windows Media Audio
    """
    AAC = 'aac'
    """
    Advanced Audio Coding
    """
    # VIDEO
    MOV = 'mov'
    """
    Apple video
    """
    MP4 = 'mp4'
    """
    MPEG-4
    """
    WEBM = 'webm'
    """
    Developed by Google, subgroup of the open and standard Matroska Video Container (MKV)
    """
    AVI = 'avi'
    """
    Audio Video Interleave
    """
    WMV = 'wmv'
    """
    Windows Media Video
    """
    AVCHD = 'avchd'
    """
    Advanced Video Coding High Definition
    """
    FVL = 'flv'
    """
    Flash Video
    """
    # SUBTITLES
    SRT = 'srt'
    """
    Srt subtitle file extension.

    This is the format:
    1
    00:00:00,000 --> 00:00:02,500
    Welcome to the Example Subtitle File!

    """
    JSON3 = 'json3'
    """
    Json3 subtitle file extension
    """
    SRV1 = 'srv1'
    """
    Srv1 subtitle file extension
    """
    SRV2 = 'srv2'
    """
    Srv2 subtitle file extension
    """
    SRV3 = 'srv3'
    """
    Srv3 subtitle file extension
    """
    TTML = 'ttml'
    """
    Ttml subtitle file extension
    """
    VTT = 'vtt'
    """
    Vtt subtitle file extension
    """
    # TEXT
    TXT = 'txt'
    """
    Txt text file extension
    """
    CSV = 'csv'
    """
    Csv text file extension
    """
    JSON = 'json'
    """
    Json text file extension
    """
    XML = 'xml'
    """
    Xml text file extension
    """
    HTML = 'html'
    """
    Html text file extension
    """
    MD = 'md'
    """
    Md text file extension
    """
    LOG = 'log'
    """
    Log text file extension
    """
    INI = 'ini'
    """
    Ini text file extension
    """
    YAML = 'yaml'
    """
    Yaml text file extension
    """
    YML = 'yml'
    """
    Yml text file extension
    """


    # TODO: Add some utils  
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, FileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)

class ImageFileExtension(Enum):
    """
    Enum class to encapsulate all existing image file extensions.
    """
    
    PNG = FileExtension.PNG.value
    """
    Portable Network Graphics
    """
    JPEG = FileExtension.JPEG.value
    """
    Joint Photographic Experts Group
    """
    JPG = FileExtension.JPG.value
    """
    Joint Photographic Experts Group
    """
    WEBP = FileExtension.WEBP.value
    """
    Web Picture
    """
    BMP = FileExtension.BMP.value
    """
    Bitmap Image File
    """
    GIF = FileExtension.GIF.value
    """
    Graphics Interchange Format
    """
    TIFF = FileExtension.TIFF.value
    """
    Tagged Image File
    """
    PSD = FileExtension.PSD.value
    """
    Photoshop Document
    """
    PDF = FileExtension.PDF.value
    """
    Portable Document Format
    """
    EPS = FileExtension.EPS.value
    """
    Encapsulated Postcript
    """
    AI = FileExtension.AI.value
    """
    Adobe Illustrator Document
    """
    INDD = FileExtension.INDD.value
    """
    Adobe Indesign Document
    """
    RAW = FileExtension.RAW.value
    """
    Raw Image Formats
    """
    CDR = FileExtension.CDR.value
    """
    Corel Draw
    """
    # TODO: Add more

    @classmethod
    def default(cls):
        return cls.PNG

    # TODO: Add some utils 
    # TODO: I cannot inherit from FileExtension Enum :( 
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, ImageFileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)

class AudioFileExtension(Enum):
    """
    Enum class to encapsulate all existing audio file extensions.
    """

    WAV = FileExtension.WAV.value
    """
    Waveform Audio
    """
    MP3 = FileExtension.MP3.value
    """
    MPEG Audio Layer 3.
    """
    M4A = FileExtension.M4A.value
    """
    MPEG-4 Audio
    """
    FLAC = FileExtension.FLAC.value
    """
    Free Lossless Audio Codec.
    """
    WMA = FileExtension.WMA.value
    """
    Windows Media Audio
    """
    AAC = FileExtension.AAC.value
    """
    Advanced Audio Coding
    """
    WEBM = FileExtension.WEBM.value
    # TODO: Add more

    @classmethod
    def default(cls):
        return cls.WAV
    
    # TODO: I cannot inherit from FileExtension Enum :( 
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, AudioFileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)

class VideoFileExtension(Enum):
    """
    Enum class to encapsulate all existing video file extensions.
    """

    MOV = FileExtension.MOV.value
    """
    Apple video
    """
    MP4 = FileExtension.MP4.value
    """
    MPEG-4
    """
    WEBM = FileExtension.WEBM.value
    """
    Developed by Google, subgroup of the open and standard Matroska Video Container (MKV)
    """
    AVI = FileExtension.AVI.value
    """
    Audio Video Interleave
    """
    WMV = FileExtension.WMV.value
    """
    Windows Media Video
    """
    AVCHD = FileExtension.AVCHD.value
    """
    Advanced Video Coding High Definition
    """
    FVL = FileExtension.FVL.value
    """
    Flash Video
    """
    # TODO: Add more

    @classmethod
    def default(cls):
        return cls.MP4
    
    # TODO: I cannot inherit from FileExtension Enum :( 
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, VideoFileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)

class SubtitleFileExtension(Enum):
    """
    Enum class to encapsulate all existing subtitle
    file extensions.
    """

    SRT = FileExtension.SRT.value
    """
    Srt subtitle file extension.

    This is the format:
    1
    00:00:00,000 --> 00:00:02,500
    Welcome to the Example Subtitle File!

    """
    JSON3 = FileExtension.JSON3.value
    """
    Json3 subtitle file extension
    """
    SRV1 = FileExtension.SRV1.value
    """
    Srv1 subtitle file extension
    """
    SRV2 = FileExtension.SRV2.value
    """
    Srv2 subtitle file extension
    """
    SRV3 = FileExtension.SRV3.value
    """
    Srv3 subtitle file extension
    """
    TTML = FileExtension.TTML.value
    """
    Ttml subtitle file extension
    """
    VTT = FileExtension.VTT.value
    """
    Vtt subtitle file extension
    """

    @classmethod
    def default(cls):
        return cls.JSON3
    
    # TODO: I cannot inherit from FileExtension Enum :( 
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, SubtitleFileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)
    
class TextFileExtension(Enum):
    """
    Enum class to encapsulate all existing text
    file extensions.
    """

    TXT = FileExtension.TXT.value
    """
    Txt subtitle file extension
    """
    JSON = FileExtension.JSON.value
    """
    Json text file extension
    """
    XML = FileExtension.XML.value
    """
    Xml text file extension
    """
    HTML = FileExtension.HTML.value
    """
    Html text file extension
    """
    MD = FileExtension.MD.value
    """
    Md text file extension
    """
    LOG = FileExtension.LOG.value
    """
    Log text file extension
    """
    INI = FileExtension.INI.value
    """
    Ini text file extension
    """
    YAML = FileExtension.YAML.value
    """
    Yaml text file extension
    """
    YML = FileExtension.YML.value
    """
    Yml text file extension
    """

    @classmethod
    def default(cls):
        return cls.TXT
    
    # TODO: I cannot inherit from FileExtension Enum :( 
    @staticmethod
    def is_filename_valid(
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, TextFileExtension)
    
    def get_temp_filename(
        self,
        filename: Union[str, None] = None
    ) -> str:
        """
        Get a temporary random filename with this file
        extension.

        The 'filename', if provided, will be forced to
        have this file extension but keeping the rest.
        If it is not provided, it will be a randomly
        generated string with this file extension.
        """
        return get_temp_filename_for_file_extension(filename, self)
    
# TODO: I've been able to inherit from another custom
# YTAEnum classes when creating a new one, but here I
# had some troubles recently so I decided to continue
# and fix it later. Please, review it and refactor
# because I'm repeating a lot of code

# These classes above should be used by the ffmpeg_handler and other
# declarations I make in our app to be consistent and reuse the code

class FileType(Enum):
    """
    Enum that represents the different file types and the valid
    extensions we accept for those file types. This Enum is to
    be used when checking filenames parameter.

    For example, we will use this to make sure the filename they
    gave to us is a video file type if we are storing a video 
    file.
    """
    IMAGE = ImageFileExtension.get_all()
    AUDIO = AudioFileExtension.get_all()
    VIDEO = VideoFileExtension.get_all()

class FileTypeX(Enum):
    """
    TODO: Check original FileType
    """

    IMAGE = 'image'
    AUDIO = 'audio'
    VIDEO = 'video'
    SUBTITLE = 'subtitle'
    TEXT = 'text'

    @staticmethod
    def get_type_from_filename(
        filename: str
    ) -> Union['FileTypeX', None]:
        for type in FileTypeX.get_all():
            if type.is_filename_valid(filename):
                return type

        return None

    def is_filename_valid(
        self,
        filename: str
    ):
        """
        Check if the provided 'filename' is valid according
        to this file extension.
        """
        return is_filename_valid_for_file_extension(filename, self.get_file_extension_enum_class())
    
    def get_file_extension_enum_class(
        self
    ) -> Union[VideoFileExtension, ImageFileExtension, AudioFileExtension]:
        """
        Get the file extension YTAEnum class associated
        with this file type YTAEnum instance.
        """
        return {
            FileTypeX.VIDEO: VideoFileExtension,
            FileTypeX.IMAGE: ImageFileExtension,
            FileTypeX.AUDIO: AudioFileExtension,
            FileTypeX.SUBTITLE: SubtitleFileExtension,
            FileTypeX.TEXT: TextFileExtension
        }[self]

    def get_default_file_extension(
        self
    ) -> Union[VideoFileExtension, ImageFileExtension, AudioFileExtension]:
        """
        Get the default file extension of this file type.
        """
        return self.get_file_extension_enum_class().default()

    def get_temp_filename(self, filename: Union[str, None]):
        """
        Get a temporary random filename for this file type.
        """
        return get_temp_filename_for_file_extension(filename, self.get_default_file_extension())

def is_filename_valid_for_file_extension(
    filename: str,
    file_extension_enum_class: Union[FileExtension, TextFileExtension, AudioFileExtension, ImageFileExtension, VideoFileExtension, SubtitleFileExtension] 
):
    """
    Check if the provided 'filename' is valid for
    the also given 'file_extension_enum_class'.
    """
    # TODO: Fix this, 'is_class' is not accepting arrays
    # if not PythonValidator.is_class(file_extension_enum_class, [FileExtension, TextFileExtension, AudioFileExtension, ImageFileExtension, VideoFileExtension, SubtitleFileExtension]):
    #     raise Exception('The "file_extension_enum" is not valid.')

    if filename is None:
        return False
    
    if not PythonValidator.is_string(filename):
        return False

    # TODO: I cannot import from 'file.filename' because of
    # cyclic import issue
    _, extension = os.path.splitext(filename)

    if '.' in extension:
        extension = extension.replace('.', '')

    if extension is None:
        return False
    
    return file_extension_enum_class.is_valid(extension)

def get_temp_filename_for_file_extension(
    filename: Union[str, None] = None,
    file_extension: Union[FileExtension, TextFileExtension, AudioFileExtension, ImageFileExtension, VideoFileExtension, SubtitleFileExtension] = FileExtension
) -> str:
    """
    Get a temporary random filename with this file
    extension.

    The 'filename', if provided, will be forced to
    have this file extension but keeping the rest.
    If it is not provided, it will be a randomly
    generated string with this file extension.
    """
    if not PythonValidator.is_instance(file_extension, [FileExtension, TextFileExtension, AudioFileExtension, ImageFileExtension, VideoFileExtension, SubtitleFileExtension]):
        raise Exception('The "file_extension_enum" is not valid.')

    filename = Temp.create_filename(f'{Random.characters()}.noext') if filename is None else filename
    filename = filename.split('.')[0] if '.' in filename else filename
    filename += f'.{file_extension.value}'

    return filename