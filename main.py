
import random
from bottle import Bottle, template, static_file, request, redirect, HTTPError

import model
import session

app = Bottle()


@app.route('/')
def index(db):
    """The home page. Will create/get cookie.
    Returns the index file with the title and
    the list of all products in the store.
    Index will iterate over the list and display
    each product.
    """
    session.get_or_create_session(db)

    info = {
        'title': "The WT Store",
        'products': model.product_list(db)
    }
    return template('index', info)


@app.route('/product/<id>')
def product(db, id):
    """The product page. Will create/get cookie
    When a product is clicked on, this page
    will diplay custom info for that product.
    If the id does not match an id in the db,
    return 404 not found
    """
    session.get_or_create_session(db)

    product = model.product_get(db, id)

    if product:
        #this product exists, to get its info.
        info = {
            'product': model.product_get(db, id)
        }
        return template('product', info)
    else:
        #no product exists, return 404
        return HTTPError(404, "No such product.")


@app.route('/cart')
def cart(db):
    """The GET cart page. Will create/get cookie
    When '/cart' is navigated to, this page will
    be displayed. It retrieves all the contents
    of the cart. The cart.html file will iterate
    over the items and display them.
    Also calculates the total amount
    """
    session.get_or_create_session(db)

    cart = session.get_cart_contents(db)

    #iterate over cart and add up the costs
    total = 0
    for item in cart:
        total=total+item['cost']

    #pass the cart and total to the cart.html
    info = {
        'title': "Current Shopping Cart contents",
        'cart': cart,
        'total': total
    }
    return template('cart', info)

@app.post('/cart')
def postcart(db):
    """The POST cart page. Will create/get cookie
    When submit is pressed on a product page, this
    will run. It will get the product id and quantity
    selected from the form. It will then add the id
    and quantity to the cart.
    Finishes by redirecting to the GET cart page
    """
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
