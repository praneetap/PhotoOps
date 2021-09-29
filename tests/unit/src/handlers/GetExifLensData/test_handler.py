# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test GetExifLensData'''

import json
import os

import pytest
import src.handlers.GetExifLensData.function as func

from dataclasses import asdict

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture(params=['GetExifLensData-event-eb.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture(params=['GetExifLensData-output.json'])
def expected_response(request):
    '''Return DDB item'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


### Tests
def test_handler(event, expected_response, mocker):
    '''Call handler'''
    resp = func.handler(event, {})
    assert asdict(resp) == expected_response

