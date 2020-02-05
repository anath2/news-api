'''
Download news data from various sources
'''

import time
import datetime as dt
from typing import List

import requests
import feedparser
from bs4 import BeautifulSoup
from sqlite3 import Connection

from . import exceptions, constants, db


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
    reuters_link = constants.FEED_URLS['reuters']
    feed = feedparser.parse(reuters_link)
    entries = feed['entries']
    result = []

    for d in entries:
        n = dict()
        text = parse_link_reuters(d['link'])

        n['title'] = d['title']
        n['text'] = text
        n['dated'] = dt.datetime.now().date().strftime(constants.DATE_FMT)

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


def get_news_from_db(date: dt.date):
    '''
    ARGS:
        conn: Database connection instance
        date: Date filter

    Get news data from database
    '''
    try:
        conn = db.get_db()
        rows = db.read_all('news', conn)
        date_str = date.strftime(constants.DATE_FMT)
        date_rows = [r for r in rows if r['dated'] == date_str]
        return date_rows
    except exceptions.DBError as err:
        raise NewsApiError(err)


def save_news_to_db(news_data: List):
    '''
    ARGS:
        news_data: A List of dictionaries containing
                   relevant news data

    Saves news to database
    '''
    try:
        conn = db.get_db()
        db.save('news', conn, news_data)
        conn.commit()
    except exceptions.DBError as err:
        conn.rollback()
        raise NewsApiError(err)
