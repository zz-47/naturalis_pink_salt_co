from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a strong secret key in production

# === Flask-Mail configuration ===
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='naturallis.pink.salt.co@gmail.com',  # Replace with your email
    MAIL_PASSWORD='usanvfaqccieitil'      # Replace with your Gmail App Password
)

mail = Mail(app)

ORDERS_FILE = 'orders.json'

# --- Product list ---
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

# Admin credentials (hardcoded for demo, use env vars for production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'All@hAll@h786'

def get_product_by_id(product_id):
    for product in products:
        if product['id'] == int(product_id):
            return product
    return None

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_order(order):
    orders = load_orders()
    orders.append(order)
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

def send_confirmation_email(to_email, name, order):
    try:
        items_str = "\n".join([
            f"{item['name']} x {item['quantity']} - ${item['subtotal']:.2f}"
            for item in order['items']
        ])
        body = f"""Hi {name},

Thank you for your order with Naturalis Pink Salt Co.

Order Details:
{items_str}

Total: ${order['total']:.2f}

We will contact you shortly for delivery.

Best regards,
Naturalis Pink Salt Co.
"""
        msg = Message(
            subject="Thank you for your order!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print("Failed to send email:", e)
        raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please login to access the dashboard.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('index'))

    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        }

    save_cart(cart)
    flash(f"Added {product['name']} to cart.", "success")
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart = get_cart()
    cart_items = []
    total = 0.0
    for pid, item in cart.items():
        product = get_product_by_id(pid)
        if product:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            cart_items.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'image': product['image'],
                'subtotal': subtotal
            })
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(cart)
        flash("Item removed from cart.", "success")
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    save_cart({})
    flash("Cart cleared.", "success")
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form.get('full-name', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        payment_method = request.form.get('payment-method', '').strip()

        if not all([name, email, address, payment_method]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('checkout'))

        cart = get_cart()
        if not cart:
            flash("Your cart is empty.", "error")
            return redirect(url_for('view_cart'))

        items = []
        total = 0.0
        for product_id, item in cart.items():
            product = get_product_by_id(product_id)
            if not product:
                continue
            quantity = item['quantity']
            subtotal = product['price'] * quantity
            items.append({
                'name': product['name'],
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal

        order = {
            'name': name,
            'email': email,
            'address': address,
            'payment_method': payment_method,
            'items': items,
            'total': total
        }

        save_order(order)

        try:
            send_confirmation_email(email, name, order)
        except Exception as e:
            print("Email sending failed:", e)
            flash("Order placed, but confirmation email could not be sent.", "warning")

        save_cart({})

        return render_template('thankyou.html')

    return render_template('checkout.html')

@app.route('/dashboard')
@login_required
def dashboard():
    orders = load_orders()
    for order in orders:
        order['total'] = order.get('total', 0.0)
        # Defensive: ensure each item has subtotal
        for item in order.get('items', []):
            if 'subtotal' not in item:
                item['subtotal'] = 0.0
    return render_template('dashboard.html', orders=orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash("Successfully logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
