from yta_file.filename.utils import sanitize_filename
from yta_file.filename.handler import FilenameHandler
from yta_constants.file import FileSearchOption, FileEncoding
from yta_validation.parameter import ParameterValidator
from yta_constants.file import FileType
from yta_validation import PythonValidator
from typing import Union
from pathlib import Path

import shutil
import os
import json
import io
import glob


# TODO: Move this method to a 'programming' module or something
def requires_dependency(
    module: str,
    library_name: Union[str, None] = None,
    package_name: Union[str, None] = None
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                __import__(module)
            except ImportError:
                message = f'The function "{func.__name__}" needs the "{module}" installed.'

                if package_name:
                    message += f" You can install it with this command: pip install {library_name}[{package_name}]"

                raise ImportError(message)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

class FileHandler:
    """
    Magic class to handle operations with files
    and folders: deleting, creating, listing, etc.
    """

    @staticmethod
    def list(
        abspath: str,
        option: FileSearchOption = FileSearchOption.FILES_AND_FOLDERS,
        pattern: str = '*',
        do_recursive: bool = False
    ) -> list:
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
        ParameterValidator.validate_mandatory_string('abspath', abspath, do_accept_empty = False)
        
        abspath = sanitize_filename(abspath)

        # This below get files and folders
        files_and_folders = [
            sanitize_filename(f)
            for f in glob.glob(pathname = abspath + pattern, recursive = do_recursive)
        ]

        return {
            FileSearchOption.FILES_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileHandler.is_file(f)
            ],
            FileSearchOption.FOLDERS_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileHandler.is_folder(f)
            ],
            FileSearchOption.FILES_AND_FOLDERS: lambda: files_and_folders
        }[option]()

    @staticmethod
    def rename_file(
        origin_filename: str,
        destination_filename: str,
    ):
        """
        Renames the 'origin_filename' to the 'destination_filename'.
        If 'replace_if_existing' is True, it will replace the destination
        file if possible and allowed. If it is False, it will fail.

        TODO: Remove 'replace_if_existing' if not used.
        """
        ParameterValidator.validate_mandatory_string('origin_filename', origin_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('destination_filename', destination_filename, do_accept_empty = False)
        
        # TODO: Implement a parameter to force overwritting
        # the destination file or not.
        
        return shutil.move(origin_filename, destination_filename)

    @staticmethod
    def copy_file(
        origin_filename: str,
        destination_filename: str
    ):
        """
        Makes a copy of the provided 'origin_filename' and 
        stores it as 'destination_filename'.

        The destination folder must exist.
        """
        ParameterValidator.validate_mandatory_string('origin_filename', origin_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('destination_filename', destination_filename, do_accept_empty = False)

        return shutil.copyfile(origin_filename, destination_filename)
    
    # Reading functionality below
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
        if (
            not PythonValidator.is_string(filename) or
            not FileHandler.file_exists(filename)
        ):
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
        if (
            not PythonValidator.is_string(filename) or
            not FileHandler.file_exists(filename)
        ):
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
        if not PythonValidator.is_string(filename) or not FileHandler.file_exists(filename):
            raise Exception('The provided "filename" is not a valid string or filename.')
        
        with open(filename, 'r', encoding = 'utf-8') as file:
            return file.read()

    @requires_dependency('pillow', 'yta_file', 'pillow')
    @requires_dependency('pydub', 'yta_file', 'pydub')
    @requires_dependency('moviepy', 'yta_file', 'moviepy')
    @staticmethod
    def parse_file_content(
        file_content: Union[bytes, bytearray, io.BytesIO],
        file_type: FileType
    ) -> Union['VideoFileClip', str, 'AudioSegment', 'Image.Image']:
        """
        Parse the provided 'file_content' with the given
        'file_type' and return that content able to be
        handled.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        from moviepy import VideoFileClip
        from pydub import AudioSegment
        from PIL import Image

        ParameterValidator.validate_mandatory_instance_of(file_content, [bytes, bytearray, io.BytesIO])
        
        file_type = FileType.to_enum(file_type)
        
        if PythonValidator.is_instance(file_content, [bytes, bytearray]):
            # If bytes, load as a file in memory
            file_content = io.BytesIO(file_content)

        parse_fn = {
            FileType.VIDEO: lambda file_content: VideoFileClip(file_content),
            FileType.SUBTITLE: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileType.TEXT: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileType.AUDIO: lambda file_content: AudioSegment.from_file(file_content),
            FileType.IMAGE: lambda file_content: Image.open(file_content)
        }.get(file_type, None)

        return (
            parse_fn(file_content)
            if parse_fn else
            None
        )

    @requires_dependency('pillow', 'yta_file', 'pillow')
    @requires_dependency('pydub', 'yta_file', 'pydub')
    @requires_dependency('moviepy', 'yta_file', 'moviepy')
    @staticmethod
    def parse_filename(
        filename: str,
    ) -> Union['VideoFileClip', str, 'AudioSegment', 'Image.Image']:
        """
        Identify the provided 'filename' extension and open
        it according to the detected file type.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        from moviepy import VideoFileClip
        from pydub import AudioSegment
        from PIL import Image

        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        reader_fn = {
            FileType.VIDEO: lambda filename: VideoFileClip(filename),
            FileType.SUBTITLE: lambda filename: FileReader.read(filename),
            FileType.TEXT: lambda filename: FileReader.read(filename),
            FileType.AUDIO: lambda filename: AudioSegment.from_file(filename),
            FileType.IMAGE: lambda filename: Image.open(filename)
        }.get(FileType.get_type_from_filename(filename), None)

        return (
            reader_fn(filename)
            if reader_fn else
            None
        )
    
    # Validation methods below
    @staticmethod
    def is_file(filename):
        """
        Checks if the provided 'filename' is an existing and
        valid file. It returns True if yes or False if not.
        """
        filename = FilenameHandler.sanitize(filename)
        filename = Path(filename)

        try:
            return (
                filename.exists()
                and filename.is_file()
            )
        except:
            # TODO: Maybe print stack (?)
            return False

    @staticmethod
    def is_folder(filename):
        """
        Checks if the provided 'filename' is an existing and
        valid folder. It returns True if yes or False if not.
        """
        filename = FilenameHandler.sanitize(filename)
        filename = Path(filename)

        try:
            return (
                filename.exists()
                and filename.is_dir()
            )
        except:
            # TODO: Maybe print stack (?)
            return False

    @staticmethod
    def file_exists(filename):
        """
        Checks if the provided 'filename' file or folder exist. It
        returns True if existing or False if not. This method
        sanitizes the provided 'filename' before checking it.
        """
        filename = FilenameHandler.sanitize(filename)

        try:
            return Path(filename).exists()
        except:
            # TODO: Maybe print stack (?)
            return False
        
    # Deleting methods below
    @staticmethod
    def delete_file(
        filename: str
    ):
        """
        Deletes the provided 'filename' if existing.

        # TODO: Maybe can be using other method that generally
        # delete files (?) Please, do if possible
        """
        if (
            not filename or
            not FileHandler.is_file(filename)
        ):
            return None
        
        os.remove(filename)

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
        # TODO: Make some risky checkings  about removing '/', '/home', etc.
        files = FileHandler.list(folder, FileSearchOption.FILES_ONLY, pattern)
        # TODO: Check what happens if deleting folders with files inside
        
        for file in files:
            os.remove(file)

    # Writing methods below
    @staticmethod
    def write_binary_file(
        binary_data: bytes,
        output_filename: str
    ) -> str:
        """
        Writes the provided 'binary_data' in the 'filename'
        file. It replaces the previous content if existing.

        This method returns the filename as written.
        """
        ParameterValidator.validate_mandatory('binary_data', binary_data)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        return _write_binary(
            binary_data,
            output_filename
        )

    @staticmethod
    def write_json_to_file(
        dict: dict,
        output_filename: str
    ) -> str:
        """
        Writes the provided 'dict' as a json into the 'filename'.

        This method returns the filename as written.

        @param
            **dict**
            Python dictionary that will be stored as a json.

            **output_filename**
            File path in which we are going to store the information.
        """
        ParameterValidator.validate_mandatory_dict('dict', dict)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        return FileHandler.write_file(
            text = json.dumps(dict, indent = 4),
            output_filename = output_filename
        )

    @staticmethod
    def write_file(
        text: str,
        output_filename: str,
        encoding: Union[str, FileEncoding, None] = FileEncoding.UTF8
    ) -> str:
        """
        Writes the provided 'text' in the 'filename' file. It
        replaces the previous content if existing.

        This method returns the filename that has been
        written.
        """
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = True)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        encoding = (
            None
            if encoding == None else
            FileEncoding.to_enum(encoding).value
        )

        return _write(text, encoding, output_filename)

    @staticmethod
    def write_file_by_chunks_from_response(
        response: 'Response',
        output_filename: str
    ) -> str:
        """
        Iterates over the provided 'response' and writes its content
        chunk by chunk in the also provided 'output_filename'.

        TODO: If you find a better way to handle this you are free to
        create new methods and move them into a new file.

        This method returns the filename that has been
        written.
        """
        ParameterValidator.validate_mandatory_instance_of('response', response, 'Response')
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        CHUNK_SIZE = 32768

        # TODO: Make this method work with a common Iterator parameter
        # and not an specific response, please
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        return output_filename
    
def _write(
    content: str,
    encoding: Union[str, FileEncoding, None],
    output_filename: str
) -> str:
    """
    Returns the 'output_filename' that has been
    written.
    """
    encoding = (
        None
        if encoding == None else
        FileEncoding.to_enum(encoding).value
    )

    with open(
        file = output_filename,
        mode = 'w',
        encoding = encoding
    ) as f:
        f.write(content)

    return output_filename

def _write_binary(
    content: bytes,
    output_filename: str
) -> str:
    """
    Returns the 'output_filename' that has been
    written.
    """
    with open(
        file = output_filename,
        mode = 'wb'
    ) as f:
        f.write(content)

    return output_filename