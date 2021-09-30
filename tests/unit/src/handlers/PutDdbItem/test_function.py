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
def item(exif_data):
    '''Return DDB item'''
    item = {
        'pk': 'bucket#object',
        'sk': 'exif#v0',
        'Exif': exif_data
    }
    return item


@pytest.fixture()
def event(item):
    '''return a test event'''
    return {'Item': item}


### AWS clients
@pytest.fixture()
def aws_credentials():
    '''Mock credentials to prevent accidentally escaping our mock'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture()
def DDB_TABLE(aws_credentials):
    '''DDB client'''
    with moto.mock_dynamodb2():
        boto3.client('dynamodb').create_table(
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
        yield boto3.resource('dynamodb').Table('TestTable')


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


