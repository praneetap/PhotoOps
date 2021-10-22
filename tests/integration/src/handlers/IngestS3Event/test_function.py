'''Test IngestS3Event'''

import json
import os

import boto3

import pytest
from aws_lambda_powertools.utilities.data_classes import S3Event

STACK_NAME = 'PhotoOps-tom'
FUNCTION_NAME = os.path.abspath(__file__).split(os.path.sep)[-2]

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

## AWS
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


### Events
@pytest.fixture()
def event():
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, 'IngestS3Event-event-sns.json')) as f:
        return json.load(f)

@pytest.fixture(params=['IngestS3Event-data-put.json', 'IngestS3Event-data-delete.json'])
def s3_notification(request):
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


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

    assert resp['StatusCode'] == 200
    assert json.loads(resp_body) == s3_notification
