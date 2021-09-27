'''Return normalized Image EXIF data'''

import json
import logging
import os

from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_exif_image_data(event: Dict[str, Any]) -> Dict[str, Any]:
    '''Return normalized image data'''

    ifd0 = event.get('Item', {}).get('IFD0', {})

    image_data = {}

    # NOTE: We need to find the IFD that holds the actual and not thumbnail data.
    image_data['FileType'] = ifd0.get('')
    image_data['SubfileType'] = ifd0.get('')
    image_data['Compression'] = ifd0.get('')
    image_data['Compressed'] = ifd0.get('')
    image_data['RAW'] = ifd0.get('')

    image_data['ImageWidth'] = ifd0.get('')
    image_data['ImageLength'] = ifd0.get('')

    # NOTE: DateTime is complicated. We should check for discrepencies between all the
    # locations and decide what to use when.
    image_data['DateTime'] = ifd0.get('DateTime')
    image_data['DateTimeOffset'] = ifd0.get('EXIF', {}).get('OffsetTime')

    image_data['AutoFocus'] = True if ifd0.get('MakerNote', {}).get('FocusMode', '').startswith('AF') else False   # Note: varies by brand.
    image_data['ExposureMode'] = ifd0.get('EXIF', {}).get('ExposureMode')
    image_data['ExposureProgram'] = ifd0.get('EXIF', {}).get('ExposureProgram')
    image_data['ExposureTime'] = ifd0.get('EXIF').get('ExposureTime')
    image_data['Flash'] = ifd0.get('EXIF', {}).get('Flash')
    image_data['FNumber'] = fd0.get('EXIF', {}).get('FNumber')
    image_data['FocalLength'] = ifd0.get('EXIF', {}).get('FocalLength')
    image_data['FocalLengthIn35mmFilm'] = ifd0.get('EXIF', {}).get('FocalLengthIn35mmFilm')
    # ISO
    # NOTE: These two tags are related but I don't know what variations exist. Also my favorite
    # line from the spec:
    #
    # "While 'Count = Any', only 1 should be used"
    image_data['PhotographicSensitivity'] = ifd0.get('EXIF', {}).get('PhotographicSensitivity', [])[0]
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
