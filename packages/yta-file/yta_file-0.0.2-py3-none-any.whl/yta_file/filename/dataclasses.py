from yta_file.filename.utils import sanitize_filename
from yta_validation.parameter import ParameterValidator
from typing import Union
from dataclasses import dataclass

import os


@dataclass
class Filename:
    """
    Dataclass to hold the information about a filename and
    its extension (if existing). This class doesn't accept
    empty strings.

    The word 'filename' is used for the file name or path
    and the extension, and the pair of words 'file name' is
    used for only the file name part (excluding the 
    extension).

    - A filename like 'test' will have file name but no 
    extension.
    - A file name like 'test.jpg' will have file name and
    extension.
    - A file name like '.gitignore' will have only the
    extension part.
    - A file name like '.config.json' will have only the
    extension part.
    """

    raw_full_filename: str
    """
    The original filename as it was detected with includes
    the file name or path and the extension (if existing).
    This string has not been sanitized.
    """
    full_filename: str
    """
    The original filename as it was detected which includes
    the file name or path and the extension (if existing).
    This string has been sanitized, which means that the
    back slashes ('\') has been turned into normal slashes
    ('/').
    """

    @property
    def has_file_name(
        self
    ) -> bool:
        """
        Boolean that indicates if the filename has a file name
        or if it is empty.
        """
        return self.original_file_name != ''

    @property
    def original_file_name(
        self
    ) -> str:
        """
        The original file name part excluding the dot and the
        extension. This can be an empty string.
        """
        return self._original_file_name
    
    @property
    def file_name(
        self
    ) -> str:
        """
        The file name part, removing the path if existing, and
        excluding the dot and the extension. This can be an
        empty string.
        """
        return self._file_name
    
    @property
    def has_extension(
        self
    ) -> bool:
        """
        Boolean that indicates if the filename has an extension.
        """
        return self.extension != ''

    @property
    def extension(
        self
    ) -> str:
        """
        The extension part, which doesn't include the dot. This
        can be an empty string.
        """
        return self._extension
    
    @property
    def filename(
        self
    ) -> str:
        """
        The file name followed by a dot and an extension (if
        existing).
        """
        return (
            f'{self.file_name}.{self.extension}'
            if self.has_extension else
            f'{self.file_name}'
        )

    @property
    def is_file_name_only(
        self
    ) -> bool:
        """
        Boolean that indicates if the filename is just a file
        name part without an extension, such as 'test'.
        """
        return (
            self.has_file_name and
            not self.has_extension
        )
    
    @property
    def is_extension_only(
        self
    ) -> bool:
        """
        Boolean that indicates if the filename is just an
        extension part without a file name, such as
        '.gitignore'.
        """
        return (
            not self.has_file_name and
            self.has_extension
        )
    
    @property
    def is_filename(
        self
    ) -> bool:
        """
        Boolean that indicates if hte filename is a whole
        filename containing a file name and an extension.
        """
        return (
            self.has_file_name and
            self.has_extension
        )

    def __init__(
        self,
        filename: str
    ):
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        self.raw_full_filename = filename
        filename = sanitize_filename(filename)
        self.origina_full_filename = filename

        # TODO: Is this (https://stackoverflow.com/a/49689414) better (?)
        filename, extension = os.path.splitext(filename)
        """
        If a 'filename' like '.gitignore' is provided, it is
        detected as the file name, but it is actually the 
        extension, so we need to handle it.
        """
        if filename.startswith('.'):
            extension = f'{filename.replace(".", "")}{extension}'
            filename = ''

        # If only filename detected but 
        self._original_file_name = filename
        aux = filename.split('/')
        self._file_name = aux[len(aux) - 1]
        # We store the extension without the dot
        self._extension = extension[1:]

    def original_file_name_with_extension(
        self,
        extension: Union[str, None]
    ) -> str:
        """
        Get the filename with the provided 'extension'. Any initial
        dot ('.') in the provided 'extension' will be ignored.
        """
        ParameterValidator.validate_mandatory_string('extension', extension, do_accept_empty = True)

        return self._with_extension(self.original_file_name, extension)

    def file_name_with_extension(
        self,
        extension: Union[str, None]
    ) -> str:
        """
        Get the filename with the provided 'extension'. Any initial
        dot ('.') in the provided 'extension' will be ignored.
        """
        ParameterValidator.validate_mandatory_string('extension', extension, do_accept_empty = True)

        return self._with_extension(self.file_name, extension)
    
    def _with_extension(
        self,
        filename: str,
        extension: str
    ) -> str:
        """
        For internal use only.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = True)
        ParameterValidator.validate_mandatory_string('extension', extension, do_accept_empty = True)

        # Remove the dot at the begining if existing
        extension = (
            extension[1:]
            if extension.startswith('.') else
            extension
        )

        return (
            f'{filename}.{extension}'
            if extension else
            f'.{filename}'
        )
