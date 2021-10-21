# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestPhoto'''

import json
import os

import boto3
import exifread
import moto
import pytest

import src.handlers.PutDdbItem.function as func

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')


@pytest.fixture(params=['PutDdbItem-event-eb.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


### AWS clients
@pytest.fixture()
def aws_credentials():
    '''Mock credentials to prevent accidentally escaping our mock'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@moto.mock_sts
@pytest.fixture()
def session(aws_credentials):
    '''AWS Session client'''
    return boto3.Session()

@pytest.fixture()
def DDB_TABLE(session):
    '''DDB client'''
    with moto.mock_dynamodb2():
        session.client('dynamodb').create_table(
            TableName='TestTable',
            KeySchema=[
                {
                    'AttributeName': 'pk',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'sk',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'pk',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'sk',
                    'AttributeType': 'S'
                }
            ]
        )
        yield session.resource('dynamodb').Table('TestTable')


### Tests
def test_handler(event, DDB_TABLE, mocker):
    '''Call handler'''

    mocker.patch.object(
        func,
        'DDB_TABLE',
        DDB_TABLE
    )

    resp = func.handler(event, {})
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200



@pytest.mark.skip(reason='Need to write')
def test_handler_unexpected_event(unexpected_event):
    '''Call handler with unexpected event data'''
    pass
#    with pytest.raises( ... ):
#        resp = func.handler(unexpected_event, {})


