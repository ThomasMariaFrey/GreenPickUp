# Imports
import sqlite3

import click
from flask import current_app, g


def get_db():
    """
    Get a database connection. If a connection does not exist in the current application context's "g" object,
    it establishes a new connection to the SQLite database specified in the current application's configuration.
    :return: The database connection (sqlite3.Connection).
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
    Close the database connection. If a connection exists in the current application context's "g" object,
    it is closed.
    :param e: The exception (optional).
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    This function reads and executes an SQL script to initialize the database tables and schema. It uses the SQLite
    database connection obtained from the "get_db" function.
    """
    db = get_db()

    with current_app.open_resource('testdatabase_init.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """
    CLI command to initialize the database.
    This command clears the existing data and creates new tables by calling the "init_db" function.
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """
    Initialize the Flask application with database-related functionality. This function sets up the database connection
    handling and adds the "init-db" CLI command to the application.
    :param app: The Flask application instance.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
