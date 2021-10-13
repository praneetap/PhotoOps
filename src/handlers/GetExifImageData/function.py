'''Return normalized Image EXIF data'''

import copy
import json
import logging
import os

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple, Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from common import ExifDataItem, Ifd, ImageExifData, ImageExifDataItem, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: ImageExifDataItem


def _get_image_info(exif: Dict[str, Any]) -> Tuple[
        Union[int, None],
        Union[int, None],
        Union[str, None],
        Union[str, None],
    ]:
    '''Get image dimensions and whether or not JPEG'''
    # Unfortunately this is the best we can do without REALLY complicating the logic. I can't
    # tell you if 'Orientation' is for the image or a thumbnail. JPEG files often drop size
    # dimension info too. We just do our best to detect signals of what the image might be.
    #
    # FIXME: this is messy and not very good.
    #
    # FIXME: We can now actually get whether the file is a JPG or not from the event.
    length = None
    width = None
    orientation = None
    compression = None

    for _k in exif:
        if None not in [length, width, orientation, compression]:
            break

        if isinstance(exif[_k], dict):
            values = _get_image_info(exif[_k])
            if length is None and values[0] is not None:
                length = values[0]
            if width is None and values[1] is not None:
                width = values[1]
            if orientation is None and values[2] is not None:
                orientation = values[2]
            if compression is None and values[3] is not None:
                compression = values[3]
        else:
            # Sometimes the JPEG thumbnails set ImageWidth and ImageLength.
            if _k in ['image_width', 'image_length'] and exif.get('subfile_type') == 'Full-resolution image':
                compression = exif.get('compression')
                if _k == 'image_width':
                    width = exif.get('image_width')
                elif _k == 'image_length':
                    length = exif.get('image_length')
            elif _k in ['pixel_x_dimension', 'pixel_y_dimension']:
                compression = exif.get('compression')
                if _k == 'pixel_x_dimension':
                    width = exif.get('pixel_x_dimension')
                elif _k == 'pixel_y_dimension':
                    length = exif.get('pixel_y_dimension')
            elif _k == 'orientation':
                orientation = exif.get('orientation')

    return (length, width, orientation, compression)


def _get_exif_image_data(exif_item: ExifDataItem) -> ImageExifData:
    '''Return normalized image data'''

    ifd0 = exif_item.exif.ifd0

    length, width, orientation, compression = _get_image_info(asdict(exif_item))

    #ifd0 = cast(Ifd, exif_item.exif.ifd0)
    image_data: Dict[str, Any] = {}

    # FIXME: Query for filetype once that data is available.
    image_data['length'] = length
    image_data['width'] = width
    image_data['orientation'] = orientation
    image_data['compression'] = compression

    # NOTE: DateTime is complicated. We should check for discrepancies between all the
    # locations and decide what to use when.
    image_data['date_time'] = ifd0.date_time
    image_data['date_time_offset'] = ifd0.exif_ifd.offset_time

    image_data['auto_focus'] = True if ifd0.maker_note.focus_mode.startswith('AF') else False
    # Note: varies by brand.
    image_data['exposure_mode'] = ifd0.exif_ifd.exposure_mode
    image_data['exposure_program'] = ifd0.exif_ifd.exposure_program
    image_data['exposure_time'] = ifd0.exif_ifd.exposure_time
    image_data['flash'] = ifd0.exif_ifd.flash
    image_data['fnumber'] = ifd0.exif_ifd.f_number
    image_data['focal_length'] = ifd0.exif_ifd.focal_length
    image_data['focal_length_in_35mm_film'] = ifd0.exif_ifd.focal_length_in_35mm_film
    # ISO
    # NOTE: These two tags are related but I don't know what variations exist. Also my favorite
    # line from the spec:
    #
    # "While 'Count = Any', only 1 should be used"
    image_data['photographic_sensitivity'] = ifd0.exif_ifd.photographic_sensitivity
    image_data['sensitivity_type'] = ifd0.exif_ifd.sensitivity_type

    image_data['light_source'] = ifd0.exif_ifd.light_source
    image_data['metering_mode'] = ifd0.exif_ifd.metering_mode
    image_data['sensing_method'] = ifd0.exif_ifd.sensing_method

    image_data['contrast'] = ifd0.exif_ifd.contrast
    image_data['gain_control'] = ifd0.exif_ifd.gain_control
    image_data['saturation'] = ifd0.exif_ifd.saturation
    image_data['sharpness'] = ifd0.exif_ifd.sharpness
    image_data['subject_distance_range'] = ifd0.exif_ifd.subject_distance_range
    image_data['white_balance'] = ifd0.exif_ifd.white_balance

    return ImageExifData(**image_data)


@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'image#v0'
    exif_item = ExifDataItem(**event)
    image_data = _get_exif_image_data(exif_item)
    image_data_item = ImageExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **image_data.__dict__
        }
    )

    response = Response(**{'Item': image_data_item})

    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
