from yta_general_utils.file.remover import FileRemover
from yta_general_utils.programming.path import get_project_abspath
from yta_general_utils.programming.env import Environment
from random import randint
from datetime import datetime

import os


class Temp:
    """
    Class to encapsulate the temp files functionality.
    """

    # TODO: I don't like the way we handle this variable
    # so please, refactor and improve it :). I would like
    # it to be a class/static property to use .WIP_FOLDER
    @staticmethod
    def WIP_FOLDER():
        """
        The Work In Progress folder in which we store all
        the temporary files we are working with. Its value
        is loaded from the '.env' 'WIP_FOLDER' variable.
        """
        # TODO: Cyclic import issue
        from yta_general_utils.file.checker import FileValidator

        WIP_FOLDER = Environment.get_current_project_env('WIP_FOLDER')
        if not WIP_FOLDER:
            # We force creating the dir
            WIP_FOLDER = get_project_abspath() + 'yta_wip/'
            if not FileValidator.is_folder(WIP_FOLDER):
                os.mkdir(WIP_FOLDER)

        return WIP_FOLDER

    # @staticmethod
    # def _initialize() -> str:
    #     """
    #     Load the current project dotenv and look for the 
    #     'WIP_FOLDER' variable definition in that file and,
    #     if not defined, set it with the default 'yta_wip'
    #     value and creates the folder if it doesn't exist.

    #     This method exist to make sure the temporary folder
    #     exist before working with it.
    #     """
    #     WIP_FOLDER = Environment.get_current_project_env('WIP_FOLDER')
    #     if not WIP_FOLDER:
    #         # We force creating the dir
    #         WIP_FOLDER = get_project_abspath() + 'yta_wip/'
    #         if not FileValidator.is_folder(WIP_FOLDER):
    #             os.mkdir(WIP_FOLDER)

    #     return WIP_FOLDER
    
    # TODO: Rename these 2 methods below please, they
    # are not very self-descriptive
    @staticmethod
    def get_filename(
        filename: str
    ) -> str:
        """
        Get a temporary file name using the given 'filename'
        and including a random suffix related to the current
        datetime. This is just a filename that doesn't 
        include the temporary folder or any prefix.

        This method uses the current datetime and a random 
        integer to be always unique.

        If you provide 'file.wav' it will return something
        similtar to 'file_202406212425.wav'.
        """
        delta = (datetime.now() - datetime(1970, 1, 1))
        aux = filename.split('.')

        return f'{aux[0]}_{str(int(delta.total_seconds()))}{str(randint(0, 10_000))}.{aux[1]}'
    
    @staticmethod
    def create_filename(
        filename: str
    ) -> str:
        """
        Get a temporary file name using the given 'filename'
        and including a random suffix related to the current
        datetime. This is a filename that includes the 
        temporary folder as a prefix so it can be used in
        the app.

        This method uses the current datetime and a random 
        integer to be always unique.

        If you provide 'file.wav' it will return something
        similtar to '$WIP_FOLDER/file_202406212425.wav'.
        """
        # TODO: Rename this as it uses wip and we do not mention it
        # TODO: Issue if no extension provided
        return Temp.create_custom_filename(Temp.get_filename(filename))
    
    @staticmethod
    def create_custom_filename(
        filename: str
    ) -> str:
        """
        Get a file name that includes the 'WIP_FOLDER' as
        a prefix but preserves the provided 'filename'. 
        This is useful when we need a temporary file to
        work with but with a specific name, maybe not for
        a long time but able to access it from different
        points of the app because of its known (and not
        random) name.
        """
        return f'{Temp.WIP_FOLDER()}{filename}'

    @staticmethod
    def initialize() -> None:
        """
        Create the folder if necessary.
        """
        Temp.WIP_FOLDER()

    @staticmethod
    def clean_folder(
        do_remove_folder: bool = True
    ) -> None:
        """
        Remove all the existing files in the temporary 
        folder.
        """
        FileRemover.delete_files(Temp.WIP_FOLDER())
        if do_remove_folder:
            os.rmdir(Temp.WIP_FOLDER())
            