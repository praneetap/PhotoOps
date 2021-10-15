'''
JPEG data classes
'''

from dataclasses import dataclass
from json_to_models.dynamic_typing import IsoTimeString

@dataclass
class JpegData:
    '''JPEG data'''
    s3_bucket: str
    s3_object_key: str
    size: int
    expiration_date_time: IsoTimeString
    original_s3_bucket: str
    original_s3_object_key: str


@dataclass
class JpegDataItem(JpegData):
    '''JPEG data DDB item'''
    pk: str = ''
    sk: str = ''