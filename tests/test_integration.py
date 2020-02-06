'''
Runs an integration test for saving news and
retrieving the result
'''

import os
import json

import pytest
import pandas as pd

from news_api import news


@pytest.fixture
def geo_db(app):
    db_file = os.path.join(app.instance_path, 'geodata.csv')
    df = pd.read_csv(db_file)
    return df


def test_news(client, geo_db):
    today_news = news.get_news_reuters()
    client.post('/news', data={'news_data': json.dumps(today_news)})
    resp = client.get('/latest')
    data = json.loads(resp.get_data(as_text=True))

    for d_out in data:
        matched = False

        for d_in in today_news:
            if all(d_in[k] == d_out[k] for k in d_in):
                matched = True

        assert matched
