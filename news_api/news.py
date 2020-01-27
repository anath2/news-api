'''
Download news data from various sources
'''

import time
import datetime as dt
from typing import List

import requests
import feedparser
from bs4 import BeautifulSoup


from . import exceptions


REUTERS_FEED_URL = 'http://feeds.reuters.com/reuters/AFRICAWorldNews'

DATE_FMT = '%Y%m%d'


def get_news_reuters() -> List:
    '''
    RETURNS:
        A list of dicts with the following keys:
            title: News headline
            text: Contents of story
            dated: when the news was retrieved

    Parses reuters RSS feed
    '''
    feed = feedparser.parse(REUTERS_FEED_URL)
    entries = feed['entries']
    result = []

    for d in entries:
        n = dict()
        text = parse_link_reuters(d['link'])

        n['title'] = d['title']
        n['text'] = text
        n['dated'] = dt.datetime.now().date().strftime(DATE_FMT)

        result.append(n)
        time.sleep(1)

    return result


def parse_link_reuters(url: str) -> str:
    '''
    ARGS:
        url: Story url
    RETURNS:
        str: News text

    Parses html from reuters news page and gets text
    using beautiful soup
    '''
    try:
        data = requests.get(url).content
        soup = BeautifulSoup(data, 'html.parser')
        paras = [p.text for p in soup.find_all('p')]
        return '\n'.join(paras)
    except Exception as err:
        raise exceptions.ScrapingError(err)
