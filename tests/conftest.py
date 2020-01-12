
import os
import pickle

import pytest


@pytest.fixture
def news_data():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, 'data')
    data_file = os.path.join(data_dir, 'news_data.pickle')

    with open(data_file, 'rb') as fd:
        data = pickle.loads(fd.read())

    return data
