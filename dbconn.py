import json
import socket
from typing import Callable

import psycopg2


def get_conn(cursor_factory=None) -> 'ConnCursor':
    """
    Returns a temporary cursor & connection to the database.
    Using this in a context manager will ensure that the connection and cursor are closed properly after use.
    Usage example (do this):
    with get_conn() as cursor:
        cursor.execute("SELECT * FROM my_table")
        results = cursor.fetchall()
        for row in results:
            print(row)
    """
    return ConnCursor(_default_conn, cursor_factory=cursor_factory)


class ConnCursor:
    def __init__(self, init_conn: Callable[[], psycopg2.extensions.connection] = None, cursor_factory=None):
        if init_conn is None:
            init_conn = lambda: _default_conn(cursor_factory)
        self.init_conn = init_conn
        self.conn = None
        self.cursor: psycopg2.extensions.cursor = None

    def __enter__(self):
        self.conn = self.init_conn()
        if self.conn is not None:
            self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
            print("Connection closed.")
        if exc_type is not None:
            print(f"An error occurred: {exc_value}")
        return False


def _default_conn(cursor_factory=None) -> psycopg2.extensions.connection:
    config = json.load(open('env.json'))
    host = config['host']
    ipv4 = socket.gethostbyname(host)
    return psycopg2.connect(
        host=config['host'],
        hostaddr=ipv4,
        user=config['user'],
        password=config['password'],
        port=config['port'],
        dbname=config['dbname'],
        cursor_factory=cursor_factory
    )
