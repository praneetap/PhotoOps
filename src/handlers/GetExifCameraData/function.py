'''Return normalized Camera EXIF data'''

import json
import logging
import os

from typing import Any, Dict, Optional

from aws_lambda_powertools.utilities.typing import LambdaContext


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_exif_camera_data(event: dict) -> Dict[str, Optional[Any]]:
    '''Return normalized camera data'''

    camera_data = {}
    camera_data['Make'] = event.get('Exif', {}).get('IFD0', {}).get('Make')
    camera_data['Model'] = event.get('Exif', {}).get('IFD0', {}).get('Model')
    camera_data['Software'] = event.get('Exif', {}).get('IFD0', {}).get('Software')
    camera_data['SerialNumber'] = event.get('Exif', {}).get('IFD0', {}).get('MakerNote', {}).get('SerialNumber')

    return camera_data


def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'camera#v0'
    camera_data = _get_exif_camera_data(event)

    response = {
        'Item': {
            'pk': pk,
            'sk': sk,
            **camera_data
        }
    }

    _logger.debug('Response: {}'.format(json.dumps(response)))

    return response
