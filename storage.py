import sqlite3
DATABASE = "telebot.db"

def get_connection(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    return connection, cursor

def close_connection(connection, cursor):
    connection.commit()
    cursor.close()
    connection.close()


def insert_place(data):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('''INSERT INTO place (name, image, latitude, longitude, user_id)
                       VALUES (?, ?, ?, ?, ?)''', data)
        print(cursor.fetchall())
    finally:
        close_connection(connection, cursor)

def insert_user(user_id):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('''INSERT INTO user
                       VALUES (?)''', user_id)
    finally:
        close_connection(connection, cursor)

def get_user(user_id):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('SELECT id FROM user WHERE id = {}'.format(user_id))
        return cursor.fetchone()

    finally:
        close_connection(connection, cursor)

def get_places_for_user(user_id):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('''SELECT id, name, image, latitude, longitude
                          FROM place WHERE user_id = {}
                          ORDER BY id DESC LIMIT 10'''.format(user_id))

        return cursor.fetchall()
    finally:
        close_connection(connection, cursor)


def delete_places_for_user(user_id):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('DELETE FROM place WHERE user_id = {}'.format(user_id))
    finally:
        close_connection(connection, cursor)

def delete_place(place_id):
    try:
        connection, cursor = get_connection(DATABASE)
        cursor.execute('DELETE FROM place WHERE id = {}'.format(place_id))
    finally:
        close_connection(connection, cursor)
