'''PhotoOpsAI photo data'''

from dataclasses import dataclass
from typing import Union


@dataclass
class PhotoData:
    '''PhotoData data'''

    file_name: str
    file_suffix: Union[str, None]
    size: int
    metadata_processed: bool

    @dataclass
    class S3Location:
        '''Image S3 location'''
        bucket: str
        key: str

    location: S3Location

