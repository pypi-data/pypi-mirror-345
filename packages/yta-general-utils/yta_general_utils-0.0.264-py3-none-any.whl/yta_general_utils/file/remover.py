from os import remove as os_remove


# TODO: Maybe move to a general FileHandler
class FileRemover:
    """
    Class to simplify and encapsulate the functionality related
    with removing files.
    """

    @staticmethod
    def delete_file(
        filename: str
    ):
        """
        Deletes the provided 'filename' if existing.

        # TODO: Maybe can be using other method that generally
        # delete files (?) Please, do if possible
        """
        # TODO: Cyclic import issue
        from yta_general_utils.file.checker import FileValidator

        if not filename or not FileValidator.is_file(filename):
            return None
        
        os_remove(filename)

    @staticmethod
    def delete_files(
        folder: str,
        pattern = '*'
    ):
        """
        Delete all the files in the 'folder' provided that match the provided
        'pattern'. The default pattern removes all existing files, so please
        use this method carefully.
        """
        # TODO: Cyclic import issue
        from yta_general_utils.file.handler import FileHandler, FileSearchOption

        # TODO: Make some risky checkings  about removing '/', '/home', etc.
        files = FileHandler.get_list(folder, FileSearchOption.FILES_ONLY, pattern)
        # TODO: Check what happens if deleting folders with files inside
        
        for file in files:
            os_remove(file)