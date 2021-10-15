'''Create JPEG image for cache'''
import io
import json
import logging
import os

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile, TemporaryFile
from typing import Any, Dict, IO

import boto3
import imageio
import rawpy

from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ParamValidationError
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import PutObjectOutputTypeDef
from mypy_boto3_sts import STSClient


from common.models import JpegData, JpegDataItem, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

S3_CLIENT: S3Client = boto3.client("s3")

# Cross account S3 access.
# try/except here for local dev and testing.
try:
    CROSS_ACCOUNT_IAM_ROLE_ARN = os.environ.get(
        'CROSS_ACCOUNT_IAM_ROLE_ARN',
        'INVALID-ARN'
    )
    STS_CLIENT: STSClient = boto3.client('sts')
    CROSS_ACCOUNT_CREDENTIALS = STS_CLIENT.assume_role(
        RoleArn=CROSS_ACCOUNT_IAM_ROLE_ARN,
        RoleSessionName=str('CreateJpegFromRaw'),
        DurationSeconds=28800   # Must be in sync with CROSS_ACCOUNT_IAM_ROLE_ARN
    ).get('Credentials', {})
    S3_CLIENT_CROSS_ACCOUNT: S3Client = boto3.client(
        "s3",
        aws_access_key_id=CROSS_ACCOUNT_CREDENTIALS['AccessKeyId'],
        aws_secret_access_key=CROSS_ACCOUNT_CREDENTIALS['SecretAccessKey'],
        aws_session_token=CROSS_ACCOUNT_CREDENTIALS['SessionToken']
    )
except ParamValidationError as e:
    pass

S3_EXPIRATION_DELTA_DAYS = 15

PHOTOOPS_S3_BUCKET = os.environ['PHOTOOPS_S3_BUCKET']
PHOTOOPS_IMAGE_CACHE_PREFIX = 'cache'


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: JpegDataItem


def _convert_raw_to_jpeg(raw_fileobj: IO[Any]) -> IO[Any]:
    '''convert a RAW image to a JPEG'''
    raw_fileobj.seek(0)
    raw = rawpy.imread(raw_fileobj)
    rgb = raw.postprocess()

    image_tmp_file = TemporaryFile('wb+')
    imageio.imwrite(image_tmp_file, rgb, format='JPEG-PIL', quality=100)

    return image_tmp_file


def _get_s3_object(s3_bucket: str, s3_object_key: str) -> IO[Any]:
    '''Get S3 object'''
    s3_object = NamedTemporaryFile('wb+')
    #s3_object = open('/tmp/foo.NEF', 'wb+')
    S3_CLIENT_CROSS_ACCOUNT.download_fileobj(
        Bucket=s3_bucket,
        Key=s3_object_key,
        Fileobj=s3_object
    )

    return s3_object


def _put_s3_object(
        s3_bucket: str,
        s3_object_key: str,
        s3_object: IO[Any],
        s3_object_expiration: datetime
    ) -> PutObjectOutputTypeDef:
    '''Put S3 object'''
    # NOTE: Not using upload_fileobj() because we want the response.
    r = S3_CLIENT.put_object(
        Bucket=s3_bucket,
        Key=s3_object_key,
        Body=s3_object,
        Expires=s3_object_expiration
    )

    return r


def _create_jpeg(s3_bucket: str, s3_object_key: str) -> JpegData:
    '''Create JPEG image'''

    original_s3_bucket = s3_bucket
    original_s3_object_key = s3_object_key
    cache_s3_bucket = PHOTOOPS_S3_BUCKET
    cache_s3_object_key = '/'.join([PHOTOOPS_IMAGE_CACHE_PREFIX, s3_bucket, s3_object_key]) + '.jpg'
    expiration = datetime.utcnow() + timedelta(days=S3_EXPIRATION_DELTA_DAYS)

    raw_image = _get_s3_object(s3_bucket, s3_object_key)
    jpeg_image = _convert_raw_to_jpeg(raw_image)
    _put_s3_object(cache_s3_bucket, cache_s3_object_key, jpeg_image, expiration)

    jpeg_data = JpegData(
        **{
            's3_bucket': cache_s3_bucket,
            's3_object_key': cache_s3_object_key,
            'original_s3_bucket': original_s3_bucket,
            'original_s3_object_key': original_s3_object_key,
            'expiration_date_time': str(expiration),
            'size': jpeg_image.tell()
        }
    )

    return jpeg_data


@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk', '')
    sk = 'jpeg#v0'
    s3_bucket, s3_object_key = pk.split('#')

    jpeg_data = _create_jpeg(s3_bucket, s3_object_key)

    response = Response(
        **{
            'Item': {
                'pk': pk,
                'sk': sk,
                **asdict(jpeg_data)
            }
        }
    )
    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response

