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
    #retrieve the current cookie (none is there isnt one)
    sessionkey = request.get_cookie(COOKIE_NAME)

    #find the corresponding sessionid in the sessions database
    cursor = db.cursor()
    sql = "SELECT sessionid FROM sessions WHERE sessionid=?"
    cursor.execute(sql, (sessionkey,))

    row = cursor.fetchone()
    if not row:
        # no existing session so create a new one
        sessionkey = uuid.uuid4().hex
        cursor = db.cursor()

        #place the new session key into sessions db
        sql = "INSERT INTO sessions (sessionid) VALUES (?)"
        cursor.execute(sql, (sessionkey,))
        db.commit()

        #set the cookie with new sessionkey and path '/'
        response.set_cookie(COOKIE_NAME, sessionkey, path='/')
    return sessionkey


def add_to_cart(db, itemid, quantity):
    """Add an item to the shopping cart"""

    #retrieve a session key
    sessionkey = get_or_create_session(db)

    #find any existing data in sessions db
    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))
    row = cursor.fetchone()

    if row['data']:
        #there is already data in sessions, so append new data to sessions db
        data = [itemid, quantity]

        #retrieve old data (ie. [[itemid, quantity]])
        olddata = json.loads(row['data'])

        #append new data
        olddata.append(data)

        # create data text (ie. '[[itemid, quantity], [itemid, quantity]]')
        data_j = json.dumps(olddata)

        #update the sessions db
        sql = "UPDATE sessions SET data = ? WHERE sessionid = ?"
        cursor.execute(sql, [data_j, sessionkey])
    else:
        #this is the first item in the cart
        #create a list within a list
        data = [[itemid, quantity]]
        data_j = json.dumps(data)

        # update the sessions db
        sql = "UPDATE sessions SET data = ? WHERE sessionid = ?"
        cursor.execute(sql, [data_j, sessionkey])

    db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """
    #retrieve a session key
    sessionkey = get_or_create_session(db)

    #find existing data
    sql = "SELECT data FROM sessions WHERE sessionid = ?"
    cursor = db.cursor()
    cursor.execute(sql, (sessionkey,))

    row = cursor.fetchone()
    if row['data']:
        #there is something in the cart
        list = json.loads(row['data'])
        cart = []

        for item in list:
            #each 'item' is an id and qty. Find each product using id
            product = model.product_get(db, item[0])
            name = product['name']
            cost = product['unit_cost']

            id = item[0]
            quantity = int(item[1]) #must be int to pass test in views
            cost = cost * float(quantity) #must be float to be multiplied by float

            #add all data to dictionary
            item = {
                'id': id,
                'quantity': quantity,
                'name': name,
                'cost': cost
            }

            #add dictionary to cart
            cart.append(item)

        return cart

    else:
        #cart is empty
        return []