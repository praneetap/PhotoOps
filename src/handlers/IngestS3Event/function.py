'''Ingest S3 event and publish event data.'''

import json
import logging
import os

from typing import Any, Dict

from aws_lambda_powertools.utilities.data_classes import SNSEvent, S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], context: LambdaContext) -> dict:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event)))

    sns_event = SNSEvent(event)
    sns_message_str = json.loads(sns_event.sns_message)
    s3_event = S3Event(sns_message_str)
    s3_event_data = s3_event._data

    _logger.debug('Response: {}'.format(json.dumps(s3_event_data)))

    resp = s3_event_data
    return resp

