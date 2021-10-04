'''Return normalized location EXIF data'''

import json
import logging
import os

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, cast

from aws_lambda_powertools.utilities.typing import LambdaContext
from common import ExifDataItem, Ifd, LocationExifData, LocationExifDataItem, PutDdbItemAction


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: LocationExifDataItem


def _get_exif_location_data(exif_data: ExifDataItem) -> LocationExifData:
    '''Return normalized location data'''
    ifd0 = cast(Ifd, exif_data.exif.ifd0)
    ifd0.gps_ifd
    location_data = {}
    location_data['gps_version_id'] = ifd0.gps_ifd.gps_version_id
    location_data['gps_latitude_ref'] = ifd0.gps_ifd.gps_latitude_ref
    location_data['gps_latitude'] = ifd0.gps_ifd.gps_latitude
    location_data['gps_longitude_ref'] = ifd0.gps_ifd.gps_longitude_ref
    location_data['gps_longitude'] = ifd0.gps_ifd.gps_longitude
    location_data['gps_altitude_ref'] = ifd0.gps_ifd.gps_altitude_ref
    location_data['gps_altitude'] = ifd0.gps_ifd.gps_altitude
    location_data['gps_time_stamp'] = ifd0.gps_ifd.gps_time_stamp
    location_data['gps_satellites'] = ifd0.gps_ifd.gps_satellites
    location_data['gps_map_datum'] = ifd0.gps_ifd.gps_map_datum
    location_data['gps_date'] = ifd0.gps_ifd.gps_date

    return LocationExifData(**location_data)


def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'location#v0'
    exif_data = ExifDataItem(**event)
    location_data = _get_exif_location_data(exif_data)
    location_data_item = LocationExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **location_data.__dict__
        }
    )

    response = Response(**{'Item': location_data_item})

    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
