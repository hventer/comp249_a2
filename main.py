
import random
from bottle import Bottle, template, static_file, request, redirect, HTTPError

import model
import session

app = Bottle()


@app.route('/')
def index(db):
    session.get_or_create_session(db)

    info = {
        'title': "The WT Store",
        'products': model.product_list(db)
    }
    return template('index', info)


@app.route('/product/<id>')
def product(db, id):
    session.get_or_create_session(db)

    product = model.product_get(db, id)

    if product:
        info = {
            'product': model.product_get(db, id)
        }
        return template('product', info)
    else:
        return HTTPError(404, "No such product.")


@app.route('/cart')
def cart(db):
    session.get_or_create_session(db)

    cart = session.get_cart_contents(db)

    info = {
        'title': "Current Shopping Cart contents",
        'cart': cart
    }

    return template('cart', info)

@app.post('/cart')
def postcart(db):
    session.get_or_create_session(db)

    product = request.forms.get('product')
    quantity = request.forms.get('quantity')

    session.add_to_cart(db, product, quantity)

    redirect("/cart")

@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')


if __name__ == '__main__':

    from bottle.ext import sqlite
    from dbschema import DATABASE_NAME
    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
    app.run(debug=True, port=8010)
