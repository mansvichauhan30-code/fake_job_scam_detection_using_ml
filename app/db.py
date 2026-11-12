"""
db.py
------
MySQL database connection helper using mysql-connector-python.

Provides a function to get a new database connection and
helper functions for executing queries.
"""

import mysql.connector
from mysql.connector import Error
from config import Config


def get_db_connection():
    """
    Create and return a new MySQL database connection.
    Raises an exception if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        raise


def execute_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Generic helper to execute a query.

    Parameters
    ----------
    query : str - SQL query with %s placeholders
    params : tuple - parameters for the query
    fetch : bool - if True, returns all rows
    fetchone : bool - if True, returns a single row
    commit : bool - if True, commits the transaction (for INSERT/UPDATE/DELETE)

    Returns
    -------
    Result of fetchall() / fetchone() / lastrowid (for inserts) / None
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    result = None

    try:
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()

        if commit:
            connection.commit()
            result = cursor.lastrowid

    finally:
        cursor.close()
        connection.close()

    return result
