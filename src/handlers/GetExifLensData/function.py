'''Return normalized Lens EXIF data'''

import json
import logging
import os

from typing import Any, Dict, List, Optional, Union

from aws_lambda_powertools.utilities.typing import LambdaContext


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def _get_lens_model(event: dict) -> str:
    '''Return lens model'''
    pass


def _get_lens_focal_attrs(ifd: dict) -> Dict[str, Union[int, float, None]]:
    '''Return lens focal attributes'''
    focal_attrs = ifd.get('MakerNote',{}).get('LensMinMaxFocalMaxAperture')
    return {
        'MinFocal': int(focal_attrs[0]),
        'MaxFocal': int(focal_attrs[1]),
        'MinAperture': None,
        'MaxApertureHigh': focal_attrs[2],
        'MaxApertureLow': focal_attrs[3],
    }



def _get_exif_lens_data(event: dict) -> Dict[str, Union[str, int, float, None, List[str]]]:
    '''Return normalized lens data'''
    ifd = event.get('Exif', {}).get('IFD0', {})

    lens_data = {
        **_get_lens_focal_attrs(ifd)
    }

    lens_data['LensMakerType'] = None
    lens_data['CameraMakerType'] = ifd.get('MakerNote', {}).get('LensType', '').split(' ')

    lens_data['AutoFocus'] = True if lens_data['CameraMakerType'][0] == 'AF' else False
    lens_data['VibrationReduction'] = True if 'VR' in lens_data['CameraMakerType'] else False

    # These are in LensData which I don't know how to read
    lens_data['Make'] = None
    lens_data['Model'] = None
    lens_data['SerialNumber'] = None
    lens_data['Macro'] = None
    lens_data['Zoom'] = True if lens_data['MinFocal'] != lens_data['MaxFocal'] else False

    return lens_data


def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'lens#v0'
    lens_data = _get_exif_lens_data(event)

    response = {
        'Item': {
            'pk': pk,
            'sk': sk,
            **lens_data
        }
    }

    _logger.debug('Response: {}'.format(json.dumps(response)))

    return response
