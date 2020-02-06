'''
Sets up application endpoints
'''

import os
import json
import datetime as dt

import pandas as pd
from flask import current_app
from flask_restful import Resource, reqparse

from . import db, news, constants


Parser = reqparse.RequestParser()

Parser.add_argument('news_data')


class DailyNews(Resource):
    '''
    Daily news data resource.
    Performs on the fly nlp operations
    '''

    def get(self):
        '''
        RETURNS:
            returns processed news daa

        Gets all saved news from db
        '''
        today = dt.datetime.now().date()
        today_news = news.get_news_from_db(today)
        today_news = self._add_location_data(today_news)
        return today_news

    @staticmethod
    def _add_location_data(news_data):
        instance_path = current_app.instance_path
        geo_file = os.path.join(instance_path, 'geodata.csv')
        geo_db = pd.read_csv(geo_file)

        return [
            {
                'locations_mentioned': news.get_locations_mentioned(n['text'], geo_db),
                **n
            }
            for n in news_data
        ]


class News(Resource):
    '''
    Retrieve all news for save a list of news stories
    to the database
    '''

    def post(self):
        '''
        Inserts a list of news stories into the db
        '''
        args = Parser.parse_args()
        json_data = args['news_data']
        data = json.loads(json_data)
        news.save_news_to_db(data)
