__version__ = '0.1.0'

import os
from typing import Dict, Optional

from flask import Flask
from flask_restful import Api

from . import resources


def create_app(test_config: Optional[Dict] = None):
    '''
    ARGS:
        test_config: A dictionary with test configurations

    Flask application factory
    '''
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'dev.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
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
