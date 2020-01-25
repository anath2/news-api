__version__ = '0.1.0'

import os
from typing import Dict, Optional

from flask import Flask
from flask_restful import Api

from . import resources


def create_app(
        app_name: str = __name__,
        test_config: Optional[Dict] = None
):
    '''
    ARGS:
        app_name: Application name
        test_config: A dictionary with test configurations

    Flask application factory
    '''
    app = Flask(__name__, instance_relative_config=True)

    config_map = {
        'development': 'dev_config.py',
        'production': 'prod_config.py'
    }

    if test_config is None:
        app.config.from_pyfile(config_map[app.env])
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:  # Ignore if exists
        pass

    # Adds api resources
    api = Api(app)
    api.add_resource(resources.News, '/news')

    # Adds application setup
    from . import db
    db.init_app(app)

    return app


def create_celery(app: Flask, celery_name: str = __name__):
    '''
    ARGS:
        app: Flask application instance
        celery_name: Celery app name

    Creates a celery instance and sets up applicatio context
    '''
    instance = Celery(
        name=celery_name,
        broker=app.config['CELERY_BROKER'],
        backend=app.config['CELERY_BACKEND']
    )

    class ContextTask(instance.Task):
        '''
        Inherits tasks and creates a cache.
        Also, wraps application context around call to task
        '''

        def __init__(self):
            self._cache = Redis.from_url(app.config['CELERY_BACKEND'])

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call(*args, **kwargs)

    instance.Task = ContextTask
    return instance
