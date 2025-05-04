from yta_file.validator import FileValidator
from yta_constants.file import FileSearchOption

import glob


class FileHandler:
    """
    Magic class to handle operations with files
    and folders: deleting, creating, listing, etc.
    """

    @staticmethod
    def get_list(
        abspath: str,
        option: FileSearchOption = FileSearchOption.FILES_AND_FOLDERS,
        pattern: str = '*',
        recursive: bool = False
    ):
        """
        List what is inside the provided 'abspath'. This method will list files and
        folders, files or only folders attending to the provided 'option'. It will
        also filter the files/folders that fit the provided 'pattern' (you can use
        '*' as wildcard, so for example '*.jpg' will list all images). This method
        can also be used in a recursive way if 'recursive' parameter is True, but
        take care of memory consumption and it would take its time to perform.

        This method returns a list with all existing elements absolute paths 
        sanitized.
        """
        if not abspath:
            return None
        
        abspath = sanitize_filename(abspath)

        # This below get files and folders
        files_and_folders = [
            sanitize_filename(f)
            for f in glob.glob(pathname = abspath + pattern, recursive = recursive)
        ]

        return {
            FileSearchOption.FILES_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileValidator.is_file(f)
            ],
            FileSearchOption.FOLDERS_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileValidator.is_folder(f)
            ],
            FileSearchOption.FILES_AND_FOLDERS: lambda: files_and_folders
        }[option]()