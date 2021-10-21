'''Test IngestS3Event'''

import base64
import json
import os

import boto3

import pytest
from aws_lambda_powertools.utilities.data_classes import S3Event

from tests.unit.src.handlers.IngestS3Event.test_function import event, s3_notification

STACK_NAME = 'PhotoOps-tom'
FUNCTION_NAME = os.path.abspath(__file__).split(os.path.sep)[-2]


@pytest.fixture()
def session():
    '''Return a boto3 session'''
    return boto3.Session()

@pytest.fixture()
def cfn_client(session):
    '''Return a CFN client'''
    return session.client('cloudformation')

@pytest.fixture()
def lambda_client(session):
    '''Return a Lambda client'''
    return session.client('lambda')


def test_handler(event, s3_notification, cfn_client, lambda_client):
    '''Test handler'''
    s3_notification_event = S3Event(s3_notification)
    event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification_event._data)

    function_info = cfn_client.describe_stack_resource(
        StackName=STACK_NAME,
        LogicalResourceId=FUNCTION_NAME
    )

    function_name = function_info['StackResourceDetail']['PhysicalResourceId']

    resp = lambda_client.invoke(
        FunctionName=function_name,
        LogType='Tail',
        Payload=json.dumps(event).encode('utf-8')
    )

    resp_body = resp.pop('Payload').read().decode()

    print(json.dumps(resp, indent=4))
    print(json.dumps(json.loads(resp_body), indent=4))
    print(base64.b64decode(resp['LogResult']).decode())