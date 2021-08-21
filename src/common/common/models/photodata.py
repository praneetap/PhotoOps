'''PhotoOpsAI photo data'''

from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class PhotoData:
    '''PhotoData data'''

    file_name: str
    file_suffix: Union[str, None]
    size: int

    @dataclass
    class S3Location:
        '''Image S3 location'''
        bucket: str
        key: str
    location: S3Location

    @dataclass
    class JpegLocation:
        '''JPEG cached image'''
        bucket: str
        key: str
        expiration: datetime
    jpeg_location: Union[JpegLocation, None] = None

    @dataclass
    class ImageData:
        '''Image data'''
        color_space: Union[str, None] = None

        @dataclass
        class Size:
            '''Image Size'''
            height: int
            width: int
        size: Union[Size, None] = None

        def __post_init__(self):
            '''Initialize child classes'''
            for attr in self.__dict__:
                if isinstance(self.__getattribute__(attr), dict):
                    if attr == 'size':
                        self.size = PhotoData.ImageData.Size(**self.size)
    image_data: Union[ImageData, None] = None

    def __post_init__(self):
        '''Initialize child classes'''
        # FIXME: Can I do this better and without cases foe each class?
        for attr in self.__dict__:
            if isinstance(self.__getattribute__(attr), dict):
                if attr == 'location':
                    self.location = PhotoData.S3Location(**self.location)
                if attr == 'jpeg_location':
                    self.jpeg_location = PhotoData.JpegLocation(**self.jpeg_location)
                if attr == 'image_data':
                    self.image_data = PhotoData.ImageData(**self.image_data)

