from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy



orders = [
    {
        'id': 1,
        'items': 'Product A, Product B',
        'total_price': 50.75,
        'customer_name': 'John Doe',
        'customer_address': '123 Main St',
        'customer_phone': '555-555-5555'
    },
]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_delivery.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String(500), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)


@app.route('/admin')
def admin():
    return render_template('admin.html', orders=orders)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']


    print(f"Product added: {name}, Description: {description}, Price: {price}")

    return redirect(url_for('admin'))

# if __name__ == '__main__':
#     app.run(debug=True)

@app.route('/')
def index():
    menu_items = MenuItem.query.all()
    return render_template('index.html', menu_items=menu_items)


@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(item_id)
    session.modified = True
    flash('Item added to cart!', 'success')
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []

    cart_items = MenuItem.query.filter(MenuItem.id.in_(session['cart'])).all()
    return render_template('cart.html', cart_items=cart_items)


@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item != item_id]
        session.modified = True
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))


@app.route('/order', methods=['POST'])
def order():
    items = request.form.getlist('items')
    total_price = sum(float(MenuItem.query.get(int(item_id)).price) for item_id in items)
    customer_name = request.form['name']
    customer_address = request.form['address']
    customer_phone = request.form['phone']

    if not customer_name or not customer_address or not customer_phone:
        flash('All fields are required!', 'danger')
    else:
        new_order = Order(items=','.join(items), total_price=total_price,
                          customer_name=customer_name, customer_address=customer_address, customer_phone=customer_phone)
        db.session.add(new_order)
        db.session.commit()
        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))

    return redirect(url_for('cart'))


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        if not name or not description or not price:
            flash('All fields are required!', 'danger')
        else:
            new_item = MenuItem(name=name, description=description, price=float(price))
            db.session.add(new_item)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('add_item.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
