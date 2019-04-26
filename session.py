"""
Code for handling sessions in our web application
"""

from bottle import request, response
import uuid
import json

import model
import dbschema

COOKIE_NAME = 'session'


def get_or_create_session(db):
    """Get the current sessionid either from a
    cookie in the current request or by creating a
    new session if none are present.

    If a new session is created, a cookie is set in the response.

    Returns the session key (string)
    """

    sessionkey = request.get_cookie(COOKIE_NAME)

    cursor = db.cursor()
    sql = "SELECT sessionid FROM sessions WHERE sessionid=?"
    cursor.execute(sql, (sessionkey,))

    row = cursor.fetchone()
    if not row:
        # no existing session so we create a new one
        sessionkey = uuid.uuid4().hex
        cursor = db.cursor()
        sql = "INSERT INTO sessions (sessionid) VALUES (?)"
        cursor.execute(sql, (sessionkey,))
        db.commit()

        response.set_cookie(COOKIE_NAME, sessionkey)

    return sessionkey


def add_to_cart(db, itemid, quantity):
    """Add an item to the shopping cart"""

    sessionkey = request.get_cookie(COOKIE_NAME)

    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))
    existing = cursor.fetchone()

    data = [itemid, quantity]
    cursor = db.cursor()
    data_j = json.dumps(data)


    if existing == []:
        sql = "INSERT INTO sessions (sessionid, data) VALUES (?, ?)"
        cursor.execute(sql, [sessionkey, data_j])
    else:
        sql = "UPDATE sessions SET data = ? WHERE sessionid = ?"
        cursor.execute(sql, [data_j, sessionkey])
    db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """

    sessionkey = request.get_cookie(COOKIE_NAME)


    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))

    result = cursor.fetchone()
    if result: #always goes into this, even when empty
        data = json.loads(result['data'])

        sql = "SELECT name FROM products WHERE id = ?"
        cursor = db.cursor()
        cursor.execute(sql, (data[0],))
        name = cursor.fetchone()

        sql = "SELECT unit_cost FROM products WHERE id = ?"
        cursor = db.cursor()
        cursor.execute(sql, (data[0],))
        cost = cursor.fetchone()

        data.append(name)
        data.append(cost)
        return data

    else:
        return []