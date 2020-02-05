'''
Application level constants
'''

SCHEMA = \
    '''
    DROP TABLE IF EXISTS news;

    CREATE TABLE news
    (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     title TEXT NOT NULL,
     text TEXT NOT NULL,
     dated TEXT NOT NULL
    );
    '''

FEED_URLS = {
    'reuters': 'http://feeds.reuters.com/reuters/AFRICAWorldNews'
}

DATE_FMT = '%Y%m%d'
