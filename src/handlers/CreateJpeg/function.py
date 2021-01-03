'''Create JPEG image for cache'''
import json
import logging
import os

from dataclasses import dataclass
from typing import Any, Dict

import boto3
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from mypy_boto3_dynamodb.type_defs import UpdateItemOutputTypeDef
from mypy_boto3_s3.type_defs import PutObjectOutputTypeDef


# This path reflects the packaged path and not repo path to the common
# package for this service.
from common import PhotoData

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

DDB = boto3.resource('dynamodb')
DDB_TABLE = DDB.Table(os.environ.get('DDB_TABLE_NAME', ''))

S3_CLIENT = boto3.client("s3")


@dataclass
class Response:
    '''Function Response'''

    jpeg_location: PhotoData.JpegLocation

    @dataclass
    class Ddb:
        '''DDB data'''
        response: UpdateItemOutputTypeDef
    ddb: Ddb


def _put_jpeg_object() -> PutObjectOutputTypeDef:
    '''Put JPEG in S3'''
    pass


def _update_item_jpeg_location() -> UpdateItemOutputTypeDef:
    '''Update photo JPEG location'''
    pass


def _create_jpeg(event: Dict[str, Any]) -> Response:
    '''Create JPEG image'''
    pass


def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    event_bridge_event = EventBridgeEvent(event)


    resp = {}


    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

