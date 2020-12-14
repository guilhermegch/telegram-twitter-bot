import sqlite3
import os.path
import datetime
import logging

# Check if database exists
def create_database():
    if not os.path.exists('database/data.db'):
        os.mkdir('database')
        conn = sqlite3.connect('database/data.db')
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                criado timestamp NOT NULL
            );"""
        )
        conn.close()
    return

# Records a new user on table
def create_user_db(username):
    
    create_database()

    # Gets the date
    data = datetime.datetime.utcnow()

    conn = sqlite3.connect('database/data.db',
                            detect_types=sqlite3.PARSE_DECLTYPES |
                            sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()

    insert = """
        INSERT INTO users (username, criado)
        VALUES (?,?);
    """

    data_tuple = (username, data)

    cursor.execute(insert, data_tuple)
    conn.commit()
    conn.close()
    
    logging.info('New user added to database')
