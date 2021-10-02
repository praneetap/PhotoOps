'''Fetch S3 object and return EXIF data item'''

# FIXME: Investigate Amazon S3 Object Lambda to replace the download.
#
# ref. https://aws.amazon.com/blogs/aws/introducing-amazon-s3-object-lambda-use-your-code-to-process-data-as-it-is-being-retrieved-from-s3/

import json
import logging
import os

from dataclasses import asdict, dataclass
from tempfile import TemporaryFile
from typing import Any, Dict

import boto3
import exifread

from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext

from common import ExifDataItem, PutDdbItemAction, make_exif_data_dataclass

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

s3_client = boto3.client('s3')


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: ExifDataItem


def _get_exif_data(s3_bucket: str, s3_object: str):
    '''Get EXIF data from object in S3'''
    with TemporaryFile('wb+') as image:
        s3_client.download_fileobj(s3_bucket, s3_object, image)
        image.seek(0)
        hdr = exifread.ExifHeader(image)
        exif_data = make_exif_data_dataclass(**hdr.dump_tag_values())

    # MakerNote data can be big
    if exif_data.ifd0 is not None:
        if exif_data.ifd0.exif_ifd is not None:
            if exif_data.ifd0.exif_ifd.maker_note is not None:
                del exif_data.ifd0.exif_ifd.maker_note

    return exif_data


def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    s3_event = S3Event(event)

    s3_bucket = s3_event.bucket_name
    s3_object = s3_event.object_key
    pk = '{}#{}'.format(s3_bucket, s3_object)
    sk = 'exif#v0'

    exif_data = _get_exif_data(s3_bucket, s3_object)
    exif_data_item = ExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            'exif': exif_data
        }
    )
    response = Response(**{'Item': exif_data_item})

    _logger.debug('EXIF: {}'.format(json.dumps(asdict(response))))

    return response
