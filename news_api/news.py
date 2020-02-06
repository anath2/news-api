'''
Download news data from various sources
'''

import time
import datetime as dt
from typing import List

import requests
import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from sqlite3 import Connection


from . import exceptions, constants, db, nlp


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


def get_locations_mentioned(news_txt: str, geo_db: pd.DataFrame) -> List:
    '''
    ARGS:
        news_txt: News text
        geo_db: The database containing geodata

    Get the list of locations mentioned in the text
    '''
    try:
        entities = nlp.get_entities(news_txt)
    except Exception as err:
        raise exceptions.NewsApiError(err)

    geo_entity_types = ['NORP', 'GPE']
    geo_entities = [e.lower() for e, t in entities if t in geo_entity_types]
    geo_entities = list(set(geo_entities))

    for _, row in geo_db.iterrows():  # Replace nationality, language etc with location
        nationality = row['nationalities'].lower()
        location = row['countries'].lower()
        geo_entities = [location if g == nationality else g for g in geo_entities]

    list_of_locations = list(geo_db['countries'].str.lower())
    geo_entities = [e for e in geo_entities if e in list_of_locations]  # Filter non nationalities
    geo_entities = list(set(geo_entities))
    return geo_entities


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
