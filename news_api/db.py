'''
Database operations. The Api uses file based db (sqlite)
'''

import sqlite3
from typing import Dict, List

import click
from flask import current_app, g, Flask
from flask.cli import with_appcontext

from . import constants, exceptions


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    '''
    Initializes database
    '''
    db = get_db()
    db.executescript(constants.SCHEMA)


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''
    Initializes database connection
    '''
    init_db()
    click.echo('Database initialized')


def get_db() -> sqlite3.Connection:
    '''
    connect to database if not in app global context otherwise,
    retreive from g
    '''
    if 'db' not in g:
        conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        conn.row_factory = sqlite3.Row
        g.db = conn

    return g.db


def close_db(e=None):
    '''
    Close database connection and remove from application context
    if present
    '''
    db = g.pop('db', None)

    if db is not None:
        db.close()


def read_all(table_name: str, conn: sqlite3.Connection) -> Dict:
    '''
    ARGS:
        table_name: Name of the table to be read
        conn: connection instance

    Read contents of data table in the database
    '''
    try:
        data = conn.execute('SELECT * FROM {};'.format(table_name)).fetchall()
        return [dict(r) for r in data]
    except sqlite3.Error as err:
        raise exceptions.DBError(err)


def save(table_name: str, conn: sqlite3.Connection, data: List[Dict]):
    '''
    ARGS:
        table_name: Name of the table to be saved to
        conn: Database connection instance
        data: A list of dictionaries to be saved to db

    Saves data in form of list of dictionaries to the database
    '''
    for row in data:
        try:
            save_row(table_name, conn, row)
        except sqlite3.Error as err:
            current_app.logger.error(err)


def save_row(table_name: str, conn: sqlite3.Connection, data: Dict):
    '''
    ARGS:
        table_name: Name of the table to be saved to
        conn: Database connection instance

    Saves dictionary to the database
    '''
    cols = list(data.keys())
    values = list(data.values())
    placeholder = ['?'] * len(cols)

    query = 'INSERT INTO {table_name} ({cols}) VALUES ({placeholder})'.format(
        table_name=table_name,
        cols=','.join(cols),
        placeholder=','.join(placeholder)
    )

    conn.execute(query, values)
