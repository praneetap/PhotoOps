# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test GetExifLocationData'''

import json
import os

import jsonschema
import pytest
import src.handlers.GetFileData.function as func

from dataclasses import asdict

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
SCHEMA_DIR = os.path.join(DATA_DIR, 'schemas')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

EVENT = os.path.join(EVENT_DIR, 'GetFileData-event-eb.json')
EVENT_SCHEMA = os.path.join(SCHEMA_DIR, 'ExifDataItem.schema.json')
RESPONSE = os.path.join(EVENT_DIR, 'GetFileData-output.json')
DATA_SCHEMA = os.path.join(SCHEMA_DIR, 'FileData.schema.json')
RESPONSE_SCHEMA = os.path.join(SCHEMA_DIR, 'GetFileDataResponse.schema.json')

### Events
@pytest.fixture()
def event(request):
    '''Return a test event'''
    with open(EVENT) as f:
        return json.load(f)


@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(EVENT_SCHEMA) as f:
        return json.load(f)


@pytest.fixture()
def expected_response(request):
    '''Return DDB item'''
    with open(RESPONSE) as f:
        return json.load(f)


@pytest.fixture()
def data_schema():
    '''Return a response schema'''
    with open(DATA_SCHEMA) as f:
        return json.load(f)


@pytest.fixture()
def response_schema():
    '''Return a response schema'''
    with open(RESPONSE_SCHEMA) as f:
        return json.load(f)


# Data validation
def test_validate_event(event, event_schema):
    '''Test event data against schema'''
    jsonschema.validate(event, event_schema)


def test_validate_expected_data(expected_response, data_schema):
    '''
    Test response data against schema

    This ensures valid data.
    '''
    jsonschema.validate(expected_response.get('Item'), data_schema)


def test_validate_expected_response(expected_response, response_schema):
    '''
    Test response against schema.

    This ensures a valid DDB PutItem body.
    '''
    # Note: This ensures { "Item": { "pk":"bucket", ""sk:"key", * } }
    jsonschema.validate(expected_response, response_schema)


### Tests
def test_handler(event, expected_response, mocker):
    '''Call handler'''
    resp = func.handler(event, {})
    assert asdict(resp) == expected_response
