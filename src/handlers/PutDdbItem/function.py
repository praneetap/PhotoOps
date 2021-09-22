'''Ingest a new photo into PhotoOps'''

import json
import logging
import os

from decimal import Decimal
from typing import Any, Dict

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import PutItemOutputTypeDef

# FIXME: Replace with powertools logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

DDB: DynamoDBServiceResource = boto3.resource('dynamodb')
DDB_TABLE: Table = DDB.Table(os.environ.get('DDB_TABLE_NAME', ''))


def _put_ddb_item(item: Dict[str, Any]) -> PutItemOutputTypeDef:
    '''Write item to DDB'''
    item['ReturnConsumedCapacity'] = 'NONE'
    response = DDB_TABLE.put_item(**item)
    _logger.debug(response)
    return response


def handler(event: Dict[str, Any], context: LambdaContext) -> PutItemOutputTypeDef:
    '''Function entry'''
    _logger.debug('Event: {}'.format(json.dumps(event, indent=4)))

    # Floats are not supported by DDB.
    event = json.loads(json.dumps(event), parse_float=Decimal)

    resp = _put_ddb_item(event)

    _logger.debug('Response: {}'.format(json.dumps(resp, indent=4)))

    return resp

