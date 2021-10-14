'''Return normalized Camera EXIF data'''

import json
import logging
import os

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, cast

from aws_lambda_powertools.utilities.typing import LambdaContext

from common.models import CameraExifData, CameraExifDataItem, ExifDataItem, Ifd, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: CameraExifDataItem


def _get_exif_camera_data(exif_data: ExifDataItem) -> CameraExifData:
    '''Return normalized camera data'''

    ifd0 = cast(Ifd, exif_data.exif.ifd0)

    camera_data = {
            'make': ifd0.make,
            'model': ifd0.model,
            'software': ifd0.software,
            'serial_number': None if ifd0.maker_note is None else ifd0.maker_note.serial_number
        }

    return CameraExifData(**camera_data)


@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'camera#v0'
    exif_data = ExifDataItem(**event)
    camera_data = _get_exif_camera_data(exif_data)
    print(camera_data.__dict__)
    camera_data_item = CameraExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **camera_data.__dict__
        }
    )

    response = Response(**{'Item': camera_data_item})

    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
