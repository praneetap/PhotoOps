'''Return normalized location EXIF data'''

import json
import logging
import os

from dataclasses import asdict, dataclass
from typing import Any, Dict, cast

from aws_lambda_powertools.utilities.typing import LambdaContext
from common import ExifDataItem, FileData, FileDataItem, PutDdbItemAction


# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: FileDataItem


def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    pk = event.get('pk')
    sk = 'file#v0'
    exif_data = ExifDataItem(**event)

    response = Response(
        **{
            'Item': {
                'pk': pk,
                'sk': sk,
                **asdict(exif_data.file)
            }
        }
    )
    _logger.debug('Response: {}'.format(json.dumps(asdict(response))))

    return response
