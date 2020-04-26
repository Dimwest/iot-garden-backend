import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
from typing import Dict
from src.log.logger import logger
from contextlib import contextmanager


@contextmanager
def get_connection(params: Dict[str, str]) -> connection:

    """
    Get a connection using a context manager.
    :param params: database connection parameters dictionary
    :return: psycopg2 connection object
    """

    try:
        conn = psycopg2.connect(**params)
        yield conn
    except Exception as e:
        logger.error(f"{str(type(e))} during database operation: {e}")
        raise e
    finally:
        # Close database connection if defined.
        logger.debug("Closing database connection")
        try:
            conn.close()
        except UnboundLocalError:
            pass


@contextmanager
def get_cursor(params: Dict[str, str], commit: bool = True) -> cursor:

    """
    Get a connection cursor using a context manager.
    :param params: database connection parameters dictionary
    :param commit: boolean determining whether changes should be committed
    :return: psycopg2 cursor object
    """

    with get_connection(params) as conn:
        # Acquire cursor from connection
        logger.debug("Obtaining database cursor.")
        cur = conn.cursor(cursor_factory=DictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            # Close cursor
            logger.debug("Closing database cursor.")
            cur.close()


def get_sensors_data(cur: psycopg2.extensions.cursor):

    """
    Fetches data from sensors' tables

    TODO -> parallelize queries

    :param cur: database cursor
    :return: JSON formatted results
    """

    data = {
        "temperature": cur.execute("SELECT * FROM sensors.temperature").fetchall(),
        "humidity": cur.execute("SELECT * FROM sensors.humidity").fetchall(),
        "light": cur.execute("SELECT * FROM sensors.light").fetchall(),
    }

    return data
