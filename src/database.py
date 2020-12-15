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

def check_user_database(username):
    conn = sqlite3.connect('file:database/data.db?mode=ro', uri=True)
    cursor = conn.cursor()
    cursor.execute("""SELECT username FROM users""")

    for user in cursor.fetchall():
        if user[0] == username:
            conn.close()
            return True
    
    conn.close()

def list_users_database():
    usernames = []
    
    conn = sqlite3.connect('file:database/data.db?mode=ro', uri=True)
    cursor = conn.cursor()
    cursor.execute("""SELECT username FROM users""")
    
    # Put usernames on a list
    for user in cursor.fetchall():
        usernames.append(user[0])
    
    # Join the list elements to create a unique message
    message = '\n'.join(usernames)

    conn.close()
    
    return message

def edit_user_database(username, new_name):
    query = """UPDATE users SET username = ? where username = ?"""

    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()

    data = (new_name, username)

    cursor.execute(query, data)
    conn.commit()     
    logging.info(f'{username} edited in database to {new_name}')

    conn.close()

def delete_user_database(username):
    query = """DELETE FROM users WHERE username = ?"""
    username = (username,)

    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()

    cursor.execute(query, username)
    conn.commit()
    logging.info(f'The user {username} was deleted from database')

    conn.close()
