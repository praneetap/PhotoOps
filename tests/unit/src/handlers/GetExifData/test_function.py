# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''test GetExifData'''

import json
import os

import boto3
import jsonschema
import exifread
import moto
import pytest

from dataclasses import asdict

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
SCHEMA_DIR = os.path.join(DATA_DIR, 'schemas')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture(params=['GetExifData-event-eb.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(SCHEMA_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=[
    'test_image_nikon.NEF',
    'test_image_lightroom_nikon.jpg',
    'test_image_lightroom_nikon.dng',
    'test_image_lightroom_nikon_embedded_raw.dng',
    'test_image_lightroom_nikon.tif',
])
def image_name(request):
    '''Return an image file object'''
    return request.param


@pytest.fixture()
def image(image_name):
    '''Return an image file object'''
    return open(os.path.join(IMAGE_DIR, image_name), 'rb')


@pytest.fixture()
def s3_bucket_name(event):
    '''S3 bucket name'''
    return event['Records'][0]['s3']['bucket']['name']


@pytest.fixture()
def s3_object_key(event):
    '''S3 bucket name'''
    return event['Records'][0]['s3']['object']['key']


@pytest.fixture()
def expected_response(image_name):
    '''Return a test event'''
    file_name = 'GetExifData-output-{}.json'.format(image_name)
    with open(os.path.join(EVENT_DIR, file_name)) as f:
        return json.load(f)


@pytest.fixture()
def response_schema():
    '''Return a response schema'''
    with open(os.path.join(SCHEMA_DIR, 'GetExifDataResponse.schema.json')) as f:
        return json.load(f)


### AWS clients
@pytest.fixture()
def aws_credentials():
    '''Mock credentials to prevent accidentally escaping our mock'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@moto.mock_s3
@pytest.fixture()
def s3_client(aws_credentials):
    '''S3 client fixture'''
    return boto3.client('s3')


@pytest.fixture()
def func(s3_client):
    '''
    Function fixture

    Ensures function initializes a mocked boto3
    '''
    import src.handlers.GetExifData.function as func
    return func


# Data validation
def test_validate_event(event, event_schema):
    '''Test event data against schema'''
    jsonschema.validate(event, event_schema)


def test_validate_expected_response(expected_response, response_schema):
    '''Test response data against schema'''
    jsonschema.validate(expected_response, response_schema)


### Tests
@moto.mock_s3
def test_handler(event, image, expected_response, s3_client, s3_bucket_name, s3_object_key, func, mocker):
    '''Call handler'''
    s3_client.create_bucket(Bucket=s3_bucket_name)

    # FIXME: How do we handle pictures
    image.seek(0)
    s3_client.upload_fileobj(image, s3_bucket_name, s3_object_key)
    # FIXME: Looks like exifread closes JPGs biut not others. Should figure that out.
    #image.seek(0)

    resp = func.handler(event, {})
    assert asdict(resp) == expected_response
