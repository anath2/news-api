'''
Sets up application endpoints
'''

import json
from flask_restful import Resource, reqparse

from . import db, exceptions


Parser = reqparse.RequestParser()
Parser.add_argument('news_data')


class News(Resource):
    '''
    Retrieve all news for save a list of news stories
    to the database
    '''

    def get(self):
        '''
        RETURNS:
            news headlines, text and date they were added

        Gets all saved news from db
        '''
        try:
            conn = db.get_db()
            rows = db.read_all('news', conn)
            return rows
        except exceptions.DBError:
            rows = []
            raise

    def post(self):
        '''
        Inserts a list of news stories into the db
        '''
        args = Parser.parse_args()
        json_data = args['news_data']
        data = json.loads(json_data)

        try:
            conn = db.get_db()
            db.save('news', conn, data)
            conn.commit()
        except exceptions.DBError:
            conn.rollback()
            raise
