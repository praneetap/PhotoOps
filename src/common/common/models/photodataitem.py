'''PhotoOpsAI photo data'''

from dataclasses import dataclass
from typing import Optional, Union

from .photodata import PhotoData


@dataclass
class PhotoDataItem(PhotoData):
    '''PhotoData DDB Item'''
    # These need values because of our sub-classing off PhotoData which has
    # default values.
    pk: str = ''
    sk: str = ''
    ttl: Optional[Union[int, None]] = None

    def __post_init__(self):
        if self.ttl is None:
            del self.ttl

