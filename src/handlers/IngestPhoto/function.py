'''Ingest a new photo into PhotoOps'''
import json
import logging
import os

from dataclasses import dataclass
from typing import Any, Dict

import boto3
from aws_lambda_powertools.utilities.data_classes import SNSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

# This path reflects the packaged path and not repo path to the common
# package for this service.
import common   # pylint: disable=unused-import

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

DDB = boto3.resource('dynamodb')
DDB_TABLE = DDB.Table(os.environ.get('DDB_TABLE_NAME', ''))

S3_CLIENT = boto3.client("s3")


@dataclass
class PhotoData:
    '''PhotoData data'''
    @dataclass
    class ExifData:
        '''Image EXIF data'''
        image: Dict[str, Any]
        gps: Dict[str, Any]
        exif: Dict[str, Any]
        maker_note: Dict[str, Any]

    exif: ExifData

    @dataclass
    class S3Location:
        '''Image S3 location'''
        bucket: str
        key: str

    location: S3Location


@dataclass
class PhotoDataItem(PhotoData):
    '''PhotoData DDB Item'''
    pk: str
    sk: str
    ttl: int


@dataclass
class Response:
    '''Function Response'''
    photo_data: PhotoDataItem
    ddb_response: Dict[str, Any]


def _create_photo_data_item(s3_location: PhotoData.S3Location,
                            exif_data: PhotoData.ExifData) -> PhotoDataItem:
    '''Create a PhotoData item from gathered data'''
    return {}



def _get_s3_object_location(s3_notification: Dict[str, Any]) -> PhotoData.S3Location:
    '''Get bucket and object key from event'''
    s3_bucket = s3_notification['Records'][0]['s3']['bucket']['name']
    s3_key = s3_notification['Records'][0]['s3']['object']['key']

    return PhotoData.S3Location(s3_bucket, s3_key)


def _get_object_exif_data(s3_location: PhotoData.S3Location) -> PhotoData.ExifData:
    '''Fetch object and return its exif data'''
    return {}


def _write_photo_data_item(photo_data_item: PhotoDataItem) -> Dict[str, Any]:
    '''Write photo to DDB'''
    return {}


def _ingest_photo(s3_notification: Dict[str, Any]) -> Response:
    s3_location = _get_s3_object_location(s3_notification)
    exif_data = _get_object_exif_data(s3_location)
    photo_data_item = _create_photo_data_item(s3_location, exif_data)

    ddb_response = _write_photo_data_item(photo_data_item)

    return {
        'photo_data': photo_data_item,
        'ddb_response': ddb_response
    }



def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))
    sns_event: SNSEvent = SNSEvent(event)

    s3_notification = json.loads(sns_event.sns_message())

    resp = _ingest_photo(s3_notification)

    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

