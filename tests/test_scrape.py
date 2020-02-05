'''
Test if data can be scraped from news sources
'''

from news_api import news


def test_reuters():
    result = news.get_news_reuters()
    assert isinstance(result, list)
    assert result

    for entry in result:
        assert sorted(list(entry.keys())) \
            == sorted(['title', 'text', 'dated'])

        for _, v in entry.items():
            assert isinstance(v, str)
