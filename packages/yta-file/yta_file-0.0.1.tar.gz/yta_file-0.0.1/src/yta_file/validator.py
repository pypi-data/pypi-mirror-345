"""
TODO: Maybe I can use other libraries more light and
set them as optional libraries so you only install
them if you want to check more exhaustively that are
valid files.
"""
from yta_file.filename import FilenameHandler
#from moviepy import AudioFileClip, VideoFileClip
#from PIL import Image
from pathlib import Path


class FileValidator:
    """
    Class to simplify and encapsulate the functionality related
    to file and folders validation.
    """

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

    # TODO: I should do this with another library to
    # avoid 'moviepy' dependency
    @staticmethod
    def file_is_audio_file(filename):
        """
        Checks if the provided 'filename' is an audio file by
        trying to instantiate it as a moviepy AudioFileClip.
        This method sanitizes the provided 'filename' before 
        checking it.
        """
        filename = FilenameHandler.sanitize(filename)

        # TODO: I'm not using moviepy to open it because it
        # creates a dependency to do only that, and it is
        # a huge problem due to incompatibilities (it is a
        # big library). I keep the code here by now.
        # try:
        #     AudioFileClip(filename)
        # except:
        #     return False

        # TODO: Check that the extension is a valid audio
        # file extension
        
        return True

    # TODO: I should do this with another library to
    # avoid 'moviepy' dependency
    @staticmethod
    def file_is_video_file(filename):
        """
        Checks if the provided 'filename' is a video file by
        trying to instantiate it as a moviepy VideoFileClip.
        This method sanitizes the provided 'filename' before
        checking it.
        """
        filename = FilenameHandler.sanitize(filename)

        # TODO: I'm not using moviepy to open it because it
        # creates a dependency to do only that, and it is
        # a huge problem due to incompatibilities (it is a
        # big library). I keep the code here by now.
        # try:
        #     VideoFileClip(filename)
        # except:
        #     return False
        
        # TODO: Check that the extension is a valid video
        # file extension
        
        return True

    @staticmethod
    def file_is_image_file(filename: str):
        """
        Checks if the provided 'filename' is a valid image
        file by opening and verifying it with the Pillow
        library.
        """
        filename = FilenameHandler.sanitize(filename)

        # TODO: I'm not using pillow to open it because it
        # creates a dependency to do only that, and it is
        # a huge problem due to incompatibilities (it is a
        # big library). I keep the code here by now.
        # try:
        #     im = Image.open(filename)
        #     im.verify()
        #     im.close()
        # except (IOError, OSError, Image.DecompressionBombError) as e:
        #     return False

        # TODO: Check that the extension is a valid image
        # file extension
            
        return True