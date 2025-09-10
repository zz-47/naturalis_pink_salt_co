from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Sample product data (12 products for 3x4 grid)
products = [
    {'id': 1, 'name': 'Pink Salt Coarse', 'price': 12.99, 'image': 'product1.jpg', 'description': 'Coarse grain natural pink salt.'},
    {'id': 2, 'name': 'Fine Pink Salt', 'price': 10.99, 'image': 'product2.jpg', 'description': 'Fine grain pink salt for cooking.'},
    {'id': 3, 'name': 'Himalayan Salt Block', 'price': 45.00, 'image': 'product3.jpg', 'description': 'Perfect for grilling and serving.'},
    {'id': 4, 'name': 'Pink Salt Grinder', 'price': 22.50, 'image': 'product4.jpg', 'description': 'Adjustable grinder with pink salt.'},
    {'id': 5, 'name': 'Salt Lamp', 'price': 55.00, 'image': 'product5.jpg', 'description': 'Natural Himalayan salt lamp.'},
    {'id': 6, 'name': 'Pink Salt Soap', 'price': 8.99, 'image': 'product6.jpg', 'description': 'Refreshing pink salt infused soap.'},
    {'id': 7, 'name': 'Bath Salts', 'price': 15.99, 'image': 'product7.jpg', 'description': 'Relaxing pink salt bath salts.'},
    {'id': 8, 'name': 'Pink Salt Scrub', 'price': 14.50, 'image': 'product8.jpg', 'description': 'Exfoliating scrub with pink salt.'},
    {'id': 9, 'name': 'Salt Inhaler', 'price': 20.00, 'image': 'product9.jpg', 'description': 'Cleanse your lungs naturally.'},
    {'id': 10, 'name': 'Salt Infused Water', 'price': 9.50, 'image': 'product10.jpg', 'description': 'Hydrating and mineral-rich.'},
    {'id': 11, 'name': 'Salt Tray', 'price': 30.00, 'image': 'product11.jpg', 'description': 'Elegant serving salt tray.'},
    {'id': 12, 'name': 'Pink Salt Candle', 'price': 25.00, 'image': 'product12.jpg', 'description': 'Scented candle with pink salt base.'}
]

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = get_cart()
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    save_cart(cart)
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart = get_cart()
    cart_items = []
    total = 0.0
    for pid, quantity in cart.items():
        product = next((p for p in products if p['id'] == int(pid)), None)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'image': product['image'],
                'total': item_total
            })
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(cart)
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    save_cart({})
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)
