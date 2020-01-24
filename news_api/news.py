'''
Download news data from various sources
'''

import time
from typing import Dict

import requests
import feedparser
from bs4 import BeautifulSoup


from . import exceptions


REUTERS_FEED_URL = 'http://feeds.reuters.com/reuters/AFRICAWorldNews'


def get_reuters_news() -> Dict:
    '''
    RETURNS:
        Dict: A dictionary with news headline and text as
        key value pairs

    Parses reuters RSS feed
    '''
    feed = feedparser.parse(REUTERS_FEED_URL)
    entries = feed['entries']
    result = {}

    for d in entries:
        text = parse_reuters_link(d['link'])
        result['title'] = text
        time.sleep(1)


def parse_reuters_link(url: str) -> str:
    try:
        data = requests.get(url).content
        soup = BeautifulSoup(data)
        paras = [p.text for p in soup.find_all('p')]
        return '\n'.join(paras)
    except Exception as err:
        raise exceptions.ScrapingError(err)
