'''
Pytest configurations
'''

import os
import pickle
import tempfile
import datetime as dt

import pytest

from news_api import create_app, db


@pytest.fixture
def data_path():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, 'data')
    return data_dir


@pytest.fixture
def news_data(data_path):
    data_file = os.path.join(data_path, 'news_data.pickle')

    with open(data_file, 'rb') as fd:
        data = pickle.loads(fd.read())

    return data


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        db.init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def client(app):
    return app.test_client()
