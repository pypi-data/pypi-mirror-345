from yta_general_utils.programming.path import get_project_abspath
from dotenv import load_dotenv

import os


class Environment:
    """
    Class to handle the environment of the project in
    which you are executing this code perfectly.
    """

    @staticmethod
    def load_current_project_dotenv():
        """
        Load the current project environment '.env' configuration
        file. The current project is the one in which the code
        is being executed (the code in which you call this method,
        not the library in which it is written).

        Any project in which you are importing this library, the
        '.env' file on its main folder will be loaded.
        """
        load_dotenv(os.path.join(get_project_abspath(), '.env'))

    @staticmethod
    def get_current_project_env(
        variable: str
    ):
        """
        Load the current project environment '.env' configuration
        file and get the value of the 'variable' if existing.

        This method makes a 'load_dotenv' call within the current
        project absolute path any time you call it, so it ensures
        the value is correctly loaded if available.

        You don't need to do 'load_dotenv()' to call this method,
        it will do for you =).
        """
        Environment.load_current_project_dotenv()

        return os.getenv(variable)
