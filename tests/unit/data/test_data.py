# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Validate PhotoOpsAI test data'''

import json
import os

import jsonschema
import pytest
from aws_lambda_powertools.utilities.data_classes import SNSEvent

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')


@pytest.fixture(params=['IngestPhoto-event-put.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture(params=['IngestPhoto-event-delete.json'])
def unexpected_event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(EVENT_DIR, 'lambda-sns-event.schema.json')) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification():
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, 'IngestPhoto-msg-put.json')) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification_from_event(event):
    '''Return an S3 notification'''
    sns_event = SNSEvent(event)
    return json.loads(sns_event.sns_message)


@pytest.fixture()
def s3_notification_schema():
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)


# Data validation
def test_validate_event_data(event, event_schema):
    '''Test event data against schema'''
    jsonschema.validate(event, event_schema)


# FIXME: We should actually be throwing and catching an error.
def test_validate_unexpected_event_data(unexpected_event, event_schema):
    '''Test unexepcted event data against schema'''
    jsonschema.validate(unexpected_event, event_schema)


def test_validate_s3_notification_data(s3_notification, s3_notification_schema):
    '''Test event data against schema'''
    jsonschema.validate(s3_notification, s3_notification_schema)


def test_validate_s3_notification_from_event_data(s3_notification_from_event, s3_notification_schema):
    '''Test event data against schema'''
    jsonschema.validate(s3_notification_from_event, s3_notification_schema)


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

