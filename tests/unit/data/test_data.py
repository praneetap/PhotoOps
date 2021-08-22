# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Validate PhotoOpsAI test data'''

import json
import os

import jsonschema
import pytest

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')


@pytest.fixture()
def event():
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, 'IngestS3Event-event-sns.json')) as f:
        return json.load(f)


@pytest.fixture()
def sns_event_schema():
    '''Return an SNS event schema'''
    with open(os.path.join(EVENT_DIR, 'lambda-sns-event.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=['IngestS3Event-data-delete.json', 'IngestS3Event-data-put.json'])
def s3_notification(request):
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification_schema():
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)


# Data validation
def test_validate_sns_event_data(event, sns_event_schema):
    '''Test event data against schema'''
    jsonschema.validate(event, sns_event_schema)


def test_validate_s3_notification_data(s3_notification, s3_notification_schema):
    '''Test event data against schema'''
    jsonschema.validate(s3_notification, s3_notification_schema)


@pytest.mark.skip(reason='Not yet written')
def test_validate_photo_data():
    '''test photo data'''
    pass

@pytest.mark.skip(reason='Not yet written')
def test_validate_photo_data_item():
    '''test photo data DDB item'''
    pass

@pytest.mark.skip(reason='Not yet written')
def test_validate_photo_image():
    '''test photo image'''
    pass

