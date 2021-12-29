"""
Define and Access the Database.
"""

import sqlite3

from flask import current_app, g


def get_db():
    """
    create a connection to a SQLite database.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    If the connection exists, it is closed.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    """
    Register with the Application.
    """
    app.teardown_appcontext(close_db)
