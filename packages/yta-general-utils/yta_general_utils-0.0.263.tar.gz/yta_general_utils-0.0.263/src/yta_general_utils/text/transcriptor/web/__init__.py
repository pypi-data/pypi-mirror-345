"""
Module to handle the html file that allows us using
the web navigator speech recognition system.

TODO: This file has to be moved to another library
and implement, if needed, the file downloading from
the new 'yta_file_downloader' library.
"""
from yta_general_utils.programming.path import get_project_abspath
from yta_general_utils.file.checker import FileValidator
from yta_general_utils.downloader import Downloader


TRANSCRIBER_HTML_FILENAME = 'index.html'
TRANSCRIBER_HTML_ABSPATH = f'{get_project_abspath()}{TRANSCRIBER_HTML_FILENAME}'

def download_web_file():
    """
    Download the html file from Google Drive if
    not available locally.
    """
    if not FileValidator.file_exists(TRANSCRIBER_HTML_ABSPATH):
        Downloader.download_google_drive_resource(
            'https://drive.google.com/file/d/1KQs6D7Zmd2Oj7mT4JTV8S38e2ITu_gUs/view?usp=sharing',
            TRANSCRIBER_HTML_FILENAME
        )