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

        response.set_cookie(COOKIE_NAME, sessionkey, path='/')
    return sessionkey


def add_to_cart(db, itemid, quantity):
    """Add an item to the shopping cart"""

    sessionkey = get_or_create_session(db)

    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))
    row = cursor.fetchone()

    if row['data']:
        data = [itemid, quantity]
        olddata = json.loads(row['data'])
        olddata.append(data)
        data_j = json.dumps(olddata)

        sql = "UPDATE sessions SET data = ? WHERE sessionid = ?"
        cursor.execute(sql, [data_j, sessionkey])
    else:
        data = [[itemid, quantity]]
        data_j = json.dumps(data)

        sql = "UPDATE sessions SET data = ? WHERE sessionid = ?"
        cursor.execute(sql, [data_j, sessionkey])

    db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """
    sessionkey = get_or_create_session(db)

    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))

    row = cursor.fetchone()
    if row['data']:
        list = json.loads(row['data'])
        cart = []

        for item in list:
            product = model.product_get(db, item[0])
            name = product['name']
            cost = product['unit_cost']

            id = item[0]
            quantity = int(item[1])
            cost = cost * float(quantity)

            item = {
                'id': id,
                'quantity': quantity,
                'name': name,
                'cost': cost
            }

            cart.append(item)

        return cart

    else:
        return []