'''Return normalized location EXIF data'''

import json
import logging
import os

from typing import Any, Dict, Optional

from aws_lambda_powertools.utilities.typing import LambdaContext


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_exif_location_data(event: dict) -> Dict[str, Optional[Any]]:
    '''Return normalized location data'''
    location_data = {}
    location_data['GPSVersionID'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSVersionID')
    location_data['GPSLatitudeRef'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLatitudeRef')
    location_data['GPSLatitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLatitude')
    location_data['GPSLongitudeRef'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLongitudeRef')
    location_data['GPSLongitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLongitude')
    location_data['GPSAltitudeRef'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSAltitudeRef')
    location_data['GPSAltitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSAltitude')
    location_data['GPSTimeStamp'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSTimeStamp')
    location_data['GPSSatellites'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSSatellites')
    location_data['GPSMapDatum'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSMapDatum')
    location_data['GPSDate'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSDate')

    return location_data


def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'location#v0'
    location_data = _get_exif_location_data(event)

    response = {
        'Item': {
            'pk': pk,
            'sk': sk,
            **location_data
        }
    }

    _logger.debug('Response: {}'.format(json.dumps(response)))

    return response
