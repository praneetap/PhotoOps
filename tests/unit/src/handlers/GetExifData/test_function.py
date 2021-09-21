# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import boto3
import moto
import pytest

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
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
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=['GetExifData-output.json'])
def exif_data(request):
    '''Return EFIX data'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@moto.mock_s3
@pytest.fixture()
def s3_client():
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

### Tests
@moto.mock_s3
def test_handler(event, exif_data, s3_client, func, mocker):
    '''Call handler'''
    s3_bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    exif_data['Item']['pk'] = '{}#{}'.format(s3_bucket_name, s3_object_key)
    exif_data['Item']['sk'] = 'exif#v0'

    s3_client.create_bucket(Bucket=s3_bucket_name)

    # FIXME: How do we handle pictures?
    with open('../../../../Pictures/Lightroom Photos/2021/09/13/_DSC0252.NEF', 'rb') as f:
        s3_client.upload_fileobj(f, s3_bucket_name, s3_object_key)
        f.seek(0)

    resp = func.handler(event, {})
    assert resp == exif_data

