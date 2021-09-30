# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''test GetExifData'''

import json
import os

import boto3
import exifread
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


@pytest.fixture(params=[
    'test_image_nikon.NEF',
    'test_image_lightroom_nikon.dng',
    'test_image_lightroom_nikon_embedded_raw.dng',
    'test_image_lightroom_nikon.tif',
])
def image(request):
    '''Return an image file object'''
    return open(os.path.join(IMAGE_DIR, request.param), 'rb')


@pytest.fixture()
def exif_data(image):
    '''Return EXIF data for an image'''
    image.seek(0)
    hdr = exifread.ExifHeader(image)
    exif_data = hdr.dump_tag_values()
    # MakerNote data can be big
    if exif_data.get('IFD0') is not None:
        if exif_data.get('IFD0').get('EXIF') is not None:
            if exif_data.get('IFD0').get('EXIF').get('MakerNote') is not None:
                del exif_data['IFD0']['EXIF']['MakerNote']
    return exif_data


@pytest.fixture()
def s3_bucket_name(event):
    '''S3 bucket name'''
    return event['Records'][0]['s3']['bucket']['name']


@pytest.fixture()
def s3_object_key(event):
    '''S3 bucket name'''
    return event['Records'][0]['s3']['object']['key']


@pytest.fixture()
def item(exif_data, s3_bucket_name, s3_object_key):
    '''Return DDB item'''
    item = {
        'pk': '{}#{}'.format(s3_bucket_name, s3_object_key),
        'sk': 'exif#v0',
        'Exif': exif_data
    }
    return item


@pytest.fixture()
def expected_response(item):
    '''Expected function response'''
    return {'Item': item}

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


### Tests
@moto.mock_s3
def test_handler(event, image, item, expected_response, s3_client, s3_bucket_name, s3_object_key, func, mocker):
    '''Call handler'''
    s3_client.create_bucket(Bucket=s3_bucket_name)

    # FIXME: How do we handle pictures
    image.seek(0)
    s3_client.upload_fileobj(image, s3_bucket_name, s3_object_key)
    image.seek(0)

    resp = func.handler(event, {})
    assert resp == expected_response

