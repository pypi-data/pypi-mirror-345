from yta_file.filename.utils import sanitize_filename
from yta_file.filename.dataclasses import Filename
from yta_constants.file import FileType
from yta_constants.file import FileExtension
from yta_validation.parameter import ParameterValidator
from typing import Union


class FilenameHandler:
    """
    Class to encapsulate and simplify the way we handle
    filenames.
    """
    def sanitize(
        filename: str
    ) -> str:
        """
        Check the provided 'filename' and transform any backslash
        character into a normal slash ('/'), returning the new
        string.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return sanitize_filename(filename)
    
    def is_filename(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a string (the path or file name)
        followed by a dot ('.') also followed by a string (the
        extension).

        Values that will be accepted:
        'C://Users/Dani/documents/test.png', 'test.jpg'.

        Values that will not be accepted:
        '.jpg', 'solounstring'
        """
        try:
            return Filename(filename).is_filename
        except:
            return False
    
    def is_filename_only(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a single string with no dot nor 
        extension.

        Values that will be accepted:
        'solounstring'

        Values that will not be accepted:
        '.jpg', 'C://Users/Dani/documents/test.png', 'test.jpg'
        """
        return Filename(filename).is_file_name_only
    
    def is_extension_only(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a single string with no dot nor 
        extension.

        Values that will be accepted:
        '.jpg'

        Values that will not be accepted:
        'solounstring', 'C://Users/Dani/documents/test.png', 'test.jpg'
        """
        return Filename(filename).is_extension_only
    
    def get_filename(
        filename: str
    ) -> str:
        """
        Get the full filename (which includes the file name, the
        dot and the extension) but removing the rest of the path
        if existing.

        This method will return, for example, 'file.txt'.
        """
        return Filename(filename).filename
    
    def get_original_filename(
        filename: str
    ) -> str:
        """
        Get the file name part only preserving the path if
        existing but removing the dot and the extension.

        This method will return, for example, 
        'C://Users/test/documents/test'
        """
        return Filename(filename).original_file_name
    
    def get_file_name(
        filename: str
    ) -> str:
        """
        Get the file name part only but removing the path
        if existing, the dot and the extension.

        This method will return, for example, 'test'.
        """
        return Filename(filename).file_name
    
    def get_extension(
        filename: str
    ) -> Union[str, None]:
        """
        Get the extension of the provided 'filename' (if
        existing) without the dot '.'.

        This method returns None if the 'filename' doesn't
        have any extension.

        TODO: Is this description above right? Should this
        method return a FileExtension enum instead of str?
        """
        return Filename(filename).extension
    
    def get_filename_and_extension(
        filename: str
    ) -> tuple[str, str]:
        """
        Get the file name and the extension of the given 'filename'
        which can be an absolute or relative path.
        """
        filename: Filename = Filename(filename)

        return (
            filename.file_name,
            filename.extension
        )
        
    def is_of_type(
        filename: str,
        type: FileType
    ) -> bool:
        """
        Checks if the provided 'filename' is a valid filename and if 
        its type is the given 'type' or not (based on the extension).
        This method will return True if the 'filename' is valid and
        belongs to the provided 'type', or False if not. It wil raise
        a Exception if something is bad formatted or missing.
        """
        filename: Filename = Filename(filename)
        type = FileType.to_enum(type)

        return type.is_filename_valid(filename.filename)

    def has_extension(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' has an extension or
        not.
        """
        return Filename(filename).has_extension
    
    def has_the_extension(
        filename: str,
        extension: FileExtension 
    ) -> bool:
        """
        Check if the provided 'filename' has the given 
        'extension' or not.
        """
        filename: Filename = Filename(filename)

        if not filename.has_extension:
            return False
        
        extension = FileExtension.to_enum(extension)

        # TODO: Maybe use the original filename instead?
        return extension.is_filename_valid(filename.filename)
    
    def force_extension(
        filename: str,
        extension: str
    ) -> str:
        """
        Force the given 'filename' to have the also provided
        'extension' by detecting the original extension and
        replacing it.

        This method will return the same string if no extension
        detected.
        """
        ParameterValidator.validate_mandatory_string('extension', extension, do_accept_empty = True)

        return Filename(filename).original_file_name_with_extension(extension)
    
    def get_filename_without_extension(
        filename: str
    ) -> str:
        """
        Get the filename (without the path if existing) without
        the extension.
        """
        return Filename(filename).file_name