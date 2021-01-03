'''Test CreateJpeg'''

import json
import os

import pytest

from src.handlers.CreateJpeg.function import handler

DATA_DIR = './data'


@pytest.fixture()
def event():
    '''Return a test event'''
    event_data = {}
    return event_data


def test_handler(event, mocker):
    '''Call handler'''
    ret = handler(event, {})

    # Add assertions below.
