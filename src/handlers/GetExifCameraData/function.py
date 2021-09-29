'''Return normalized Camera EXIF data'''

import json
import logging
import os

from dataclasses import asdict
from typing import Any, Dict, Optional

from aws_lambda_powertools.utilities.typing import LambdaContext

from common import CameraExifData, CameraExifDataItem, CameraExifDataResponse


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_exif_camera_data(event: dict) -> CameraExifData:
    '''Return normalized camera data'''

    camera_data = CameraExifData(
        **{
            'make': event.get('Exif', {}).get('IFD0', {}).get('Make'),
            'model': event.get('Exif', {}).get('IFD0', {}).get('Model'),
            'software': event.get('Exif', {}).get('IFD0', {}).get('Software'),
            'serial_number': event.get('Exif', {}).get('IFD0', {}).get('MakerNote', {}).get('SerialNumber')
        }
    )

    return camera_data


def handler(event: Dict[str, Any], context: LambdaContext) -> CameraExifDataResponse:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'camera#v0'
    camera_data = _get_exif_camera_data(event)
    camera_data_item = CameraExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **camera_data.__dict__
        }
    )

    response = CameraExifDataResponse(**{'Item': camera_data_item})

    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
