'''Return normalized location EXIF data'''

import json
import logging
import os

from dataclasses import asdict
from typing import Any, Dict, Optional

from aws_lambda_powertools.utilities.typing import LambdaContext
from common import LocationExifData, LocationExifDataItem, LocationExifDataResponse


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_exif_location_data(event: dict) -> LocationExifData:
    '''Return normalized location data'''
    location_data = {}
    location_data['gps_version_id'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSVersionID', [])
    location_data['gps_latitude_ref'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLatitudeRef')
    location_data['gps_latitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLatitude')
    location_data['gps_longitude_ref'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLongitudeRef')
    location_data['gps_longitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSLongitude')
    location_data['gps_altitude_ref'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSAltitudeRef')
    location_data['gps_altitude'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSAltitude')
    location_data['gps_timestamp'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSTimeStamp')
    location_data['gps_satellites'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSSatellites')
    location_data['gps_map_datum'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSMapDatum')
    location_data['gps_date'] = event.get('Exif', {}).get('IFD0', {}).get('GPS', {}).get('GPSDate')

    return LocationExifData(**location_data)


def handler(event: Dict[str, Any], context: LambdaContext) -> LocationExifDataResponse:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'location#v0'
    location_data = _get_exif_location_data(event)
    location_data_item = LocationExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **location_data.__dict__
        }
    )

    response = LocationExifDataResponse(**{'Item': location_data_item})

    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
