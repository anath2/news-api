'''
Sets up application endpoints
'''

import json
import datetime as dt
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
        return news.get_news_from_db(today)


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
