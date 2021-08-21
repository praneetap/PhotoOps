'''Create JPEG image for cache'''
import io
import json
import logging
import os

from dataclasses import asdict
from datetime import timedelta
from typing import Any, Dict

import boto3
import rawpy
from aws_lambda_powertools.utilities.typing import LambdaContext
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import PutObjectOutputTypeDef
from PIL import Image


# This path reflects the packaged path and not repo path to the common
# package for this service.
from common import PhotoDataItem

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

S3_CLIENT: S3Client = boto3.client("s3")
S3_CACHE_PREFIX = 'cache'
S3_EXPIRATION_DELTA_DAYS = 15


def _convert_raw_to_jpeg(raw_fileobj: io.BytesIO):
    '''convert a RAW image to a JPEG'''
    raw = rawpy.imread(raw_fileobj)
    rgb = raw.postprocess()
    image = Image.fromarray(rgb)

    return image


def _get_s3_object(location: PhotoDataItem.S3Location) -> io.BytesIO:
    '''Get S3 object'''
    s3_object = io.BytesIO()
    S3_CLIENT.download_fileobj(
        Bucket=location.bucket,
        Key=location.key,
        Fileobj=s3_object
    )

    return s3_object


def _put_s3_object(
    location: PhotoDataItem.JpegLocation,
    fileobj: io.BytesIO,
) -> PutObjectOutputTypeDef:
    '''Put S3 object'''
    # NOTE: Not using upload_fileobj() because we want the response.
    r = S3_CLIENT.put_object(
        Bucket=location.bucket,
        Key=location.key,
        Body=fileobj,
        Expires=location.expiration
    )

    return r


def _create_jpeg(photo_item: PhotoDataItem) -> PhotoDataItem:
    '''Create JPEG image'''

    raw_image = _get_s3_object(photo_item.location)
    jpeg_image = _convert_raw_to_jpeg(raw_image)

    jpeg_location: PhotoDataItem.JpegLocation = {
        'bucket': photo_item.image_location.bucket,
        'key': photo_item.image_location.key,
        'expiration': timedelta(days=S3_EXPIRATION_DELTA_DAYS)
    }

    s3_response = _put_s3_object(jpeg_location, jpeg_image)
    _logger.debug('_create_jpeg() s3_response: {0}'.format(s3_response))

    photo_item.jpeg_location = jpeg_location

    return photo_item


def handler(event: Dict[str, Any], context: LambdaContext) -> PhotoDataItem:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    photo_item = PhotoDataItem(**asdict(event))

    resp = _create_jpeg(photo_item)

    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

