'''
Test api and end points
'''

import json
import pprint
import datetime as dt
from news_api import __version__, create_app


def test_version():
    assert __version__ == '0.1.0'


def test_app_config(app):
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


class TestEndpoints:

    def test_get_news(self, client):
        resp = client.get('/news')
        data = json.loads(resp.get_data(as_text=True))
        assert data
        assert isinstance(data, list)

    def test_post_news(self, client, news_data):
        today = dt.datetime.now().strftime('%Y%m%d')
        news_data = [{'title': t, 'text': d, 'dated': today} for t, d in news_data.items()]
        client.post('/news', data={'news_data': json.dumps(news_data)})
        resp = client.get('/news')
        data = json.loads(resp.get_data(as_text=True))
        assert data
        pprint.pprint(data)
        assert isinstance(data, list)
