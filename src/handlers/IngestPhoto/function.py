'''Ingest a new photo into PhotoOps'''
import json
import logging
import os

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union

import boto3
from aws_lambda_powertools.utilities.data_classes import SNSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from mypy_boto3_dynamodb.type_defs import PutItemOutputTypeDef

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


@dataclass
class PhotoDataItem(PhotoData):
    '''PhotoData DDB Item'''
    pk: str
    sk: str
    ttl: Optional[Union[int, None]] = None

    def __post_init__(self):
        if self.ttl is None:
            del self.ttl


@dataclass
class Response:
    '''Function Response'''
    photo_data: PhotoData
    ddb_response: PutItemOutputTypeDef


def _get_photo_data(s3_notification: Dict[str, Any]) -> PhotoData:
    '''Create a PhotoData item from gathered data'''
    s3_location = _get_s3_object_location(s3_notification)
    # FIXME: Can't assume a single '.' in file.
    file_name, *tmp_file_suffix = os.path.basename(s3_location.key).split('.')
    file_suffix = tmp_file_suffix[0] or None
    size = s3_notification['Records'][0]['s3']['object']['size'] or 0  # Making mypy happy

    return PhotoData(
        file_name=file_name,
        file_suffix=file_suffix,
        location=s3_location,
        size=size,
        metadata_processed=False
    )


def _get_s3_object_location(s3_notification: Dict[str, Any]) -> PhotoData.S3Location:
    '''Get bucket and object key from event'''
    s3_bucket = s3_notification['Records'][0]['s3']['bucket']['name']
    s3_key = s3_notification['Records'][0]['s3']['object']['key']

    return PhotoData.S3Location(s3_bucket, s3_key)


def _write_photo_data_item(photo_data: PhotoData) -> PutItemOutputTypeDef:
    '''Write photo to DDB'''
    pk = 'PHOTO#{0}#{1}'.format(photo_data.location.bucket, photo_data.location.key)
    # FIXME: revisit what sort key should be.
    sk = 'v0'

    photo_data_item = PhotoDataItem(
        pk=pk,
        sk=sk,
        **asdict(photo_data)
    )

    response = DDB_TABLE.put_item(
        Item=asdict(photo_data_item)
    )

    return response


def _ingest_photo(s3_notification: Dict[str, Any]) -> Response:
    photo_data = _get_photo_data(s3_notification)
    ddb_response = _write_photo_data_item(photo_data)

    return Response(
        photo_data=photo_data,
        ddb_response=ddb_response
    )


def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    sns_event = SNSEvent(event)
    s3_notification = json.loads(sns_event.sns_message)
    resp = _ingest_photo(s3_notification)

    _logger.debug('Response: {}'.format(json.dumps(asdict(resp))))
    return resp

