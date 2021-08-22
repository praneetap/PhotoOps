# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import pytest

from aws_lambda_powertools.utilities.data_classes import S3Event

import src.handlers.IngestS3Event.function as func

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture()
def event():
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, 'IngestS3Event-event-sns.json')) as f:
        return json.load(f)

@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(EVENT_DIR, 'lambda-sns-event.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=['IngestS3Event-data-put.json', 'IngestS3Event-data-delete.json'])
def s3_notification(request):
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification_schema():
    '''Return an S3 notification schema'''
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)



### Tests
def test_handler(event, s3_notification, mocker):
    '''Call handler'''

    s3_notification_event = S3Event(s3_notification)
    event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification_event._data)

    resp = func.handler(event, {})

    assert resp == s3_notification

