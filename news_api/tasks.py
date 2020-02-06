'''
Initializes tasks to be run with celery
'''

import json
import pickle
from typing import List

import requests
from flask import current_app
from celery.schedules import crontab

from . import (
    create_app,
    create_celery,
    exceptions,
    news
)


APP = create_app(app_name='celery_app')

CELERY = create_celery(APP, celery_name='celery')


@CELERY.on_after_configure.connect
def setup_tasks(sender, **kwargs):
    sender.add_periodic_task(APP.config['UPDATE_NEWS_PERIOD'], update_news_reuters, name='update-news-reuters')


class NewsTask(CELERY.Task):
    '''
    Tasks associated with retrieveing news data from sources
    '''

    _EXCEPTION_THRESHOLD = 4

    _RETRY_IN = 60  # Seconds

    def __init__(self):
        super().__init__()
        self._exception_count = 0
        self._cache['NEWS'] = bytes()

    def __call__(self, *args, **kwargs):
        # Retry multiple times in case of exception before failing
        while True:
            try:
                super().__call__(*args, **kwargs)
                self._exception_count = 0
                break
            except exceptions.NewsApiError as err:
                if self._exception_count == self._EXCEPTION_THRESHOLD:
                    current_app.logger.error('Maximum tries exceeded')
                    current_app.logger.error(err)
                    break
                else:
                    self._exception_count += 1
                    current_app.logger.warning('Failed, retrying in %s seconds', self._RETRY_IN)
                    time.sleep(self._RETRY_IN)

    @property
    def cached_news(self):
        '''
        Gets news dat stored in cache
        '''
        try:
            news_data = pickle.loads(self._cache['NEWS'])
        except EOFError:
            news_data = {}

        return news_data

    def save_news(self, news_data: List):
        '''
        Saves a list of dicts as bytes into redis
        '''
        pck = pickle.dumps(news_data)
        self._cache['NEWS'] = pck


@CELERY.task(bind=True, base=NewsTask)
def update_news_reuters(self):
    '''
    Get latest news data from reuters
    '''
    APP.logger.info('Getting cached news...')
    previous = self.cached_news

    APP.logger.info('Downloading news from reuters...')
    new_news = news.get_news_reuters()
    self.save_news(new_news)

    prev_titles = set([n['title'] for n in previous])
    updates = [s for s in new_news if s['title'] not in prev_titles]
    APP.logger.info('Saving news to db...')
    requests.post('{}/news'.format(APP.config['APP_HOST']), data={'news_data': json.dumps(updates)})
