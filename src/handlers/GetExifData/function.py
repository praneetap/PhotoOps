'''Fetch S3 object and return EXIF data item'''

# FIXME: Investigate Amazon S3 Object Lambda to replace the download.
#
# ref. https://aws.amazon.com/blogs/aws/introducing-amazon-s3-object-lambda-use-your-code-to-process-data-as-it-is-being-retrieved-from-s3/

import json
import logging
import os

from dataclasses import asdict, dataclass
from tempfile import TemporaryFile
from typing import Any, Dict, Tuple

import boto3
import exifread
import filetype

from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ParamValidationError
from mypy_boto3_s3 import S3Client
from mypy_boto3_sts import STSClient

from common.models import ExifDataItem, FileData, PutDdbItemAction, make_exif_data_dataclass
from common.util.dataclasses import lambda_dataclass_response

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

CROSS_ACCOUNT_IAM_ROLE_ARN = os.environ.get('CROSS_ACCOUNT_IAM_ROLE_ARN')


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: ExifDataItem


def _get_cross_account_s3_client() -> S3Client:
    '''Return an S3 Client with cross account credentials.'''
    sts_client: STSClient = boto3.client('sts')
    cross_account_credentials = sts_client.assume_role(
        RoleArn=CROSS_ACCOUNT_IAM_ROLE_ARN,
        RoleSessionName=str('GetExifData'),
    ).get('Credentials', {})
    s3_client_cross_account: S3Client = boto3.client(
        "s3",
        aws_access_key_id=cross_account_credentials['AccessKeyId'],
        aws_secret_access_key=cross_account_credentials['SecretAccessKey'],
        aws_session_token=cross_account_credentials['SessionToken']
    )

    return s3_client_cross_account


def _get_exif_data(s3_bucket: str, s3_object: str, object_size: int) -> Tuple[Any, FileData]:
    '''Get EXIF data from object in S3'''
    with TemporaryFile('wb+') as image:
        s3_cross_account_client = _get_cross_account_s3_client()
        s3_cross_account_client.download_fileobj(s3_bucket, s3_object, image)
        image.seek(0)
        ft: filetype.Type = filetype.guess(image)
        # FIXME: hdr has an open file handle. Will closing it reduce memory
        # footprint? Should ExifRead close it? Probably not the more I think of it. That
        # means JPEG handling, which closes it, is broken. Perhaps we delete the object at
        # end of this clause.
        image.seek(0)
        hdr = exifread.ExifHeader(image)
        exif_data = make_exif_data_dataclass(**hdr.dump_tag_values())

    # MakerNote data can be big
    if exif_data.ifd0 is not None:
        if exif_data.ifd0.exif_ifd is not None:
            if exif_data.ifd0.exif_ifd.maker_note is not None:
                del exif_data.ifd0.exif_ifd.maker_note



    if ft.extension == 'tif':
        file_type = 'TIFF'
    elif ft.extension == 'jpg':
        file_type = 'JPEG'
    else:
        file_type = ft.extension.upper()

    file_name_split = s3_object.split('.')
    if len(file_name_split) == 1:
        extension = None
    else:
        extension = file_name_split[-1].lower()

    if file_type == 'JPEG':
        is_jpeg = True
    else:
        is_jpeg = False

    if file_type == 'TIFF' and extension in ['tif', 'tiff']:
        is_raw = False
    elif file_type == 'TIFF':
        is_raw = True
    else:
        is_raw = False


    file_data = FileData(**{
        'file_type': file_type,
        'extension': extension,
        'object_size': object_size,
        'is_jpeg': is_jpeg,
        'is_raw': is_raw,
    })

    return exif_data, file_data

@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    s3_event = S3Event(event)

    s3_bucket = s3_event.bucket_name
    s3_object = s3_event.object_key
    object_size = s3_event.record.s3.get_object.size
    pk = '{}#{}'.format(s3_bucket, s3_object)
    sk = 'exif#v0'

    (exif_data, file_data) = _get_exif_data(s3_bucket, s3_object, object_size)
    exif_data_item = ExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            'file': file_data,
            'exif': exif_data
        }
    )
    response = Response(**{'Item': exif_data_item})

    _logger.debug('EXIF: {}'.format(json.dumps(asdict(response))))

    return response
