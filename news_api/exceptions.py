'''
Exception classes
'''

class NewsApiError(Exception):
    '''
    Exception base class
    '''


class DBError(NewsApiError):
    '''
    Error reading from or writing to database
    '''


class ConnectionError(NewsApiError):
    '''
    Error occurring establishing connection
    to the API
    '''


class NLPError(NewsApiError):
    '''
    Errors analysing text data
    '''


class ScrapingError(NewsApiError):
    '''
    Errors retreiving data from news sources
    '''
