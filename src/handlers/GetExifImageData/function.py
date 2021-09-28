'''Return normalized Image EXIF data'''

import json
import logging
import os

from typing import Any, Dict, Tuple, Union
from xmlrpc.client import Boolean

from aws_lambda_powertools.utilities.typing import LambdaContext


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_image_info(exif: Dict[str, Any]) -> Tuple[
        Union[int, None],
        Union[int, None],
        Union[str, None],
        Union[str, None],
        bool
    ]:
    '''Get image dimensions and whether or not JPEG'''
    # Unfortunately this is the best we can do without REALLY complicating the logic. I can't
    # tell you if 'Orientation' is for the image or a thumbnail. JPEG files often drop size
    # dimension info too. We just do our best to detect signals of what the image might be.
    #
    # FIXME: this is messy and not very good.
    length = None
    width = None
    orientation = None
    compression = None
    is_jpeg = True  # JPEGs are a crapshoot for having dimension info so assume is JPEG until 
                    # shown otherwise.

    for _k in exif:
        #print(_k)
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
            if not values[4]:
                is_jpeg = values[4]
        else:
            # Sometimes the JPEG thumbnails set ImageWidth and ImageLength.
            if _k in ['ImageWidth', 'ImageLength'] and exif.get('SubfileType') == 'Full-resolution image':
                compression = exif.get('Compression')
                is_jpeg = False
                if _k == 'ImageWidth':
                    width = exif.get('ImageWidth')
                elif _k == 'ImageLength':
                    length = exif.get('ImageLength')
            elif _k in ['PixelXDimension', 'PixelYDimension']:
                compression = exif.get('Compression')
                if _k == 'PixelXDimension':
                    width = exif.get('PixelXDimension')
                elif _k == 'PixelYDimension':
                    length = exif.get('PixelYDimension')
            elif _k == 'Orientation':
                orientation = exif.get('Orientation')

    return (length, width, orientation, compression, is_jpeg)


def _get_exif_image_data(event: Dict[str, Any]) -> Dict[str, Any]:
    '''Return normalized image data'''

    exif = event.get('Exif', {})
    ifd0 = exif.get('IFD0', {})
    image_data: Dict[str, Any] = {}

    length, width, orientation, compression, is_jpeg = _get_image_info(exif)
    image_data['Length'] = length
    image_data['Width'] = width
    image_data['Orientation'] = orientation
    image_data['Compression'] = compression
    image_data['JPEG'] = is_jpeg

    file_split = event.get('pk', '').split('.')
    print(file_split)
    if len(file_split) == 1:
        image_data['FileType'] = 'UNKNOWN'
    else:
        file_extension = file_split[-1].upper()
        if file_extension in ['JPEG', 'JPG']:
            image_data['FileType'] = 'JPEG'
        elif file_extension in ['TIFF', 'TIF']:
            image_data['FileType'] = 'TIFF'
        else:
            image_data['FileType'] = file_extension

    # NOTE: DateTime is complicated. We should check for discrepancies between all the
    # locations and decide what to use when.
    image_data['DateTime'] = ifd0.get('DateTime')
    image_data['DateTimeOffset'] = ifd0.get('EXIF', {}).get('OffsetTime')

    image_data['AutoFocus'] = True if ifd0.get('MakerNote', {}).get('FocusMode', '').startswith('AF') else False   # Note: varies by brand.
    image_data['ExposureMode'] = ifd0.get('EXIF', {}).get('ExposureMode')
    image_data['ExposureProgram'] = ifd0.get('EXIF', {}).get('ExposureProgram')
    image_data['ExposureTime'] = ifd0.get('EXIF', {}).get('ExposureTime')
    image_data['Flash'] = ifd0.get('EXIF', {}).get('Flash')
    image_data['FNumber'] = ifd0.get('EXIF', {}).get('FNumber')
    image_data['FocalLength'] = ifd0.get('EXIF', {}).get('FocalLength')
    image_data['FocalLengthIn35mmFilm'] = ifd0.get('EXIF', {}).get('FocalLengthIn35mmFilm')
    # ISO
    # NOTE: These two tags are related but I don't know what variations exist. Also my favorite
    # line from the spec:
    #
    # "While 'Count = Any', only 1 should be used"
    image_data['PhotographicSensitivity'] = ifd0.get('EXIF', {}).get('PhotographicSensitivity', [])
    image_data['SensitivityType'] = ifd0.get('EXIF', {}).get('SensitivityType')

    image_data['LightSource'] = ifd0.get('EXIF', {}).get('LightSource')
    image_data['MeteringMode'] = ifd0.get('EXIF', {}).get('MeteringMode')
    image_data['SensingMethod'] = ifd0.get('EXIF', {}).get('SensingMethod')

    image_data['Contrast'] = ifd0.get('EXIF', {}).get('Contrast')
    image_data['GainControl'] = ifd0.get('EXIF', {}).get('GainControl')
    image_data['Saturation'] = ifd0.get('EXIF', {}).get('Saturation')
    image_data['Sharpness'] = ifd0.get('EXIF', {}).get('Sharpness')
    image_data['SubjectDistanceRange'] = ifd0.get('EXIF', {}).get('SubjectDistanceRange')
    image_data['WhiteBalance'] = ifd0.get('EXIF', {}).get('WhiteBalance')

    return image_data


def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'image#v0'
    image_data = _get_exif_image_data(event)

    p = (pk, sk)
    response = {
        'Item': {
            'pk': pk,
            'sk': sk,
            **image_data
        }
    }

    _logger.debug('Response: {}'.format(json.dumps(response)))

    return response
