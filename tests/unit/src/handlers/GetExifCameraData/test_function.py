# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import jsonschema
import pytest
import src.handlers.GetExifCameraData.function as func

from dataclasses import asdict

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
SCHEMA_DIR = os.path.join(DATA_DIR, 'schemas')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture(params=['GetExifCameraData-event-eb.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(SCHEMA_DIR, 'ExifDataItem.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=['GetExifCameraData-output.json'])
def expected_response(request):
    '''Return DDB item'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def response_schema():
    '''Return a response schema'''
    with open(os.path.join(SCHEMA_DIR, 'GetExifCameraDataResponse.schema.json')) as f:
        return json.load(f)


# Data validation
def test_validate_event(event, event_schema):
    '''Test event data against schema'''
    jsonschema.validate(event, event_schema)


def test_validate_expected_response(expected_response, response_schema):
    '''Test response data against schema'''
    jsonschema.validate(expected_response, response_schema)


### Tests
def test_handler(event, expected_response, mocker):
    '''Call handler'''
    resp = func.handler(event, {})
    assert asdict(resp) == expected_response
