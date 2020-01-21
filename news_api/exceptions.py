'''
Exception classes
'''

class NewsApiError(Exception):
    '''
    Exception base class
    '''


class DBError(NewsApiError):
    '''
    Error reading from or writing to DB
    '''
