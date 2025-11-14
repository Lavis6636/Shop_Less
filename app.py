import json
import os
import logging
from datetime import datetime
from functools import wraps
import uuid
from sqlalchemy.dialects.postgresql import JSON, UUID



import joblib
import numpy as np

from flask import (
    Flask, render_template, request, redirect, url_for, session, jsonify, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure blockchain.py is importable
try:
    from blockchain import Blockchain
except ImportError:
    print("FATAL ERROR: Could not import Blockchain from blockchain.py. Please ensure the file is present.")
    exit()

# Set up logging
logging.basicConfig(level=logging.INFO)

# ---------------- App & DB setup ----------------
app = Flask(__name__)
app.secret_key = 'shop-less-secret-key-2024'

# Use os.path.join for robust path handling
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'shopless.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- Blockchain init ----------------
blockchain = Blockchain()

# ---------------- Product Catalog ----------------
PRODUCT_CATALOG = [
    {'sku': 'ipx', 'name': 'iPhone X', 'series': 'X', 'base_price': 5000.00, 'image': 'iPhone X.jpg'},
    {'sku': 'ipxs', 'name': 'iPhone XS', 'series': 'X', 'base_price': 5200.00, 'image': 'iPhone Xs.jpg'},
    {'sku': 'ipxsmax', 'name': 'iPhone XS Max', 'series': 'X', 'base_price': 5500.00, 'image': 'iPhone Xs Max.jpg'},
    {'sku': 'ip11', 'name': 'iPhone 11', 'series': '11', 'base_price': 6000.00, 'image': 'iPhone 11.jpg'},
    {'sku': 'ip11pro', 'name': 'iPhone 11 Pro', 'series': '11', 'base_price': 7000.00, 'image': 'iPhone 11 Pro.jpg'},
    {'sku': 'ip11promax', 'name': 'iPhone 11 Pro Max', 'series': '11', 'base_price': 8000.00, 'image': 'iPhone 11 Pro Max.jpg'},
    {'sku': 'ip12', 'name': 'iPhone 12', 'series': '12', 'base_price': 7000.00, 'image': 'iPhone 12.jpg'},
    {'sku': 'ip12mini', 'name': 'iPhone 12 mini', 'series': '12', 'base_price': 6800.00, 'image': 'iPhone 12 mini.jpg'},
    {'sku': 'ip12pro', 'name': 'iPhone 12 Pro', 'series': '12', 'base_price': 8500.00, 'image': 'iPhone 12 Pro.jpg'},
    {'sku': 'ip12promax', 'name': 'iPhone 12 Pro Max', 'series': '12', 'base_price': 9000.00, 'image': 'iPhone 12 Pro Max.jpg'},
    {'sku': 'ip13', 'name': 'iPhone 13', 'series': '13', 'base_price': 8000.00, 'image': 'iPhone 13.jpg'},
    {'sku': 'ip13mini', 'name': 'iPhone 13 mini', 'series': '13', 'base_price': 7800.00, 'image': 'iPhone 13 mini.jpg'},
    {'sku': 'ip13pro', 'name': 'iPhone 13 Pro', 'series': '13', 'base_price': 9500.00, 'image': 'iPhone 13 Pro.jpg'},
    {'sku': 'ip13promax', 'name': 'iPhone 13 Pro Max', 'series': '13', 'base_price': 10000.00, 'image': 'iPhone 13 Pro Max.jpg'},
    {'sku': 'ip14', 'name': 'iPhone 14', 'series': '14', 'base_price': 9000.00, 'image': 'iPhone 14.jpg'},
    {'sku': 'ip14plus', 'name': 'iPhone 14 Plus', 'series': '14', 'base_price': 9200.00, 'image': 'iPhone 14 Plus.jpg'},
    {'sku': 'ip14pro', 'name': 'iPhone 14 Pro', 'series': '14', 'base_price': 11000.00, 'image': 'iPhone 14 Pro.jpg'},
    {'sku': 'ip14promax', 'name': 'iPhone 14 Pro Max', 'series': '14', 'base_price': 12000.00, 'image': 'iPhone 14 Pro Max.jpg'},
    {'sku': 'ip15', 'name': 'iPhone 15', 'series': '15', 'base_price': 10000.00, 'image': 'iPhone 15.jpg'},
    {'sku': 'ip15plus', 'name': 'iPhone 15 Plus', 'series': '15', 'base_price': 10200.00, 'image': 'iPhone 15 Plus.jpg'},
    {'sku': 'ip15pro', 'name': 'iPhone 15 Pro', 'series': '15', 'base_price': 12500.00, 'image': 'iPhone 15 Pro.jpg'},
    {'sku': 'ip15promax', 'name': 'iPhone 15 Pro Max', 'series': '15', 'base_price': 14000.00, 'image': 'iPhone 15 Pro Max.jpg'},
    {'sku': 'ip16', 'name': 'iPhone 16', 'series': '16', 'base_price': 11000.00, 'image': 'iPhone 16.jpg'},
    {'sku': 'ip16pro', 'name': 'iPhone 16 Pro', 'series': '16', 'base_price': 14000.00, 'image': 'iPhone 16 Pro.jpg'},
    {'sku': 'ip16promax', 'name': 'iPhone 16 Pro Max', 'series': '16', 'base_price': 16000.00, 'image': 'iPhone 16 Pro Max.jpg'},
    {'sku': 'ip17', 'name': 'iPhone 17', 'series': '17', 'base_price': 12000.00, 'image': 'iPhone 17.jpg'},
    {'sku': 'ip17pro', 'name': 'iPhone 17 Pro', 'series': '17', 'base_price': 15500.00, 'image': 'iPhone 17 Pro.jpg'},
    {'sku': 'ip17promax', 'name': 'iPhone 17 Pro Max', 'series': '17', 'base_price': 18000.00, 'image': 'iPhone 17 Pro Max.jpg'},
]

# Placeholder for a simple blockchain module/class if it's external
class SimpleBlockchain:
    def __init__(self):
        self.chain = [{'index': 1, 'timestamp': str(datetime.now()), 'transactions': [], 'proof': 100, 'previous_hash': '1'}]
        self.current_transactions = []
    @property
    def last_block(self): return self.chain[-1]
    def new_transaction(self, sender, recipient, amount, items):
        self.current_transactions.append({'sender': sender, 'recipient': recipient, 'amount': amount, 'items': items})
        return self.last_block['index'] + 1
    def new_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1, 'timestamp': str(datetime.now()), 'transactions': self.current_transactions, 'proof': proof, 'previous_hash': previous_hash}
        self.current_transactions = []
        self.chain.append(block)
        return block
    def proof_of_work(self, last_proof): return 42 # Simplified PoW
    def hash(self, block): return json.dumps(block, sort_keys=True).encode() # Simplified hash
    def valid_chain(self, chain): return True
blockchain = SimpleBlockchain()
BASEDIR = os.path.abspath(os.path.dirname(__file__))
# --- End Global Configuration ---


STORAGE_MULTIPLIERS = {'64GB': 1.0, '128GB': 1.25, '256GB': 1.5}

# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)
    password = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    series = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def price(self):
        return self.base_price

    def __repr__(self):
        return f'<Product {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skus = db.Column(db.Text, nullable=False)  # Comma-separated SKUs
    items = db.Column(JSON, nullable=False)    # List of items (JSON)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



# ---------------- AI Model Loading ----------------
sales_model = None
le_product = None
le_series = None

MODEL_PATH = os.path.join(BASEDIR, 'model/sales_predictor.pkl')
PRODUCT_ENCODER_PATH = os.path.join(BASEDIR, 'model/product_encoder.pkl')
SERIES_ENCODER_PATH = os.path.join(BASEDIR, 'model/series_encoder.pkl')

def load_ai_model():
    """Loads the trained model and encoders from the 'model' directory."""
    global sales_model, le_product, le_series
    
    try:
        if not os.path.exists(MODEL_PATH):
            # No need to raise, just log and continue if the model is optional
            logging.warning("❌ AI Model file not found. Skipping model loading.")
            return
            
        sales_model = joblib.load(MODEL_PATH)
        le_product = joblib.load(PRODUCT_ENCODER_PATH)
        le_series = joblib.load(SERIES_ENCODER_PATH)
        logging.info("✅ AI Sales Model and Encoders Loaded Successfully.")
    except FileNotFoundError:
        logging.warning("❌ AI Model files not found. Run train_sales_model.py first to enable predictions.")
    except Exception as e:
        logging.error(f"❌ Error loading AI Model: {e}")

# Call the loading function
load_ai_model()

# ---------------- Database Initialization (Moved to main run block) ----------------

# ---------------- Decorators & Context Processors ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def global_context():
    """
    Injects common variables into all templates:
    - current_user: username
    - current_role: user role
    - cart: session cart data
    - total_items: total quantity in cart
    - total_price: grand total of cart
    - products: full product catalog
    """
    # User info
    current_user = session.get('username')
    current_role = session.get('role')

    # Cart info
    cart = session.get('cart', {})
    total_items = sum(item.get('quantity', 0) for item in cart.values())
    total_price = sum(float(item.get('total_price', 0.0)) for item in cart.values())

    # Products (for nav, sidebars, etc.)
    products = Product.query.all() if Product.query.count() else PRODUCT_CATALOG

    return dict(
        current_user=current_user,
        current_role=current_role,
        cart=cart,
        total_items=total_items,
        total_price=total_price,
        products=products
    )

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}



# ---------------- Routes ----------------

from config.security import SecurityConfig, permission_required


@app.route('/')
def home():  # rename function to 'home'
    return render_template('index.html', products=PRODUCT_CATALOG)

@app.route('/products')
def products():
    return render_template('products.html', products=PRODUCT_CATALOG)

@app.route('/product/<string:product_sku>')
def product_detail(product_sku):
    # Find the product by SKU
    product = next((p for p in PRODUCT_CATALOG if p['sku'] == product_sku), None)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))

    return render_template(
        'product_detail.html',
        product=product,
        multipliers=STORAGE_MULTIPLIERS  # <-- Pass it here
    )

# ---------------- CART ROUTES USING SKU ----------------
@app.route('/add_to_cart/<string:product_sku>', methods=['POST'])
@login_required
def add_to_cart(product_sku):
    """
    Adds the selected product and configuration to the session-based cart.
    """
    product = next((p for p in PRODUCT_CATALOG if p['sku'] == product_sku), None)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))

    storage = request.form.get('storage')
    quantity_str = request.form.get('quantity', '1')

    try:
        quantity = int(quantity_str)
        if quantity < 1:
            raise ValueError
    except ValueError:
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('product_detail', product_sku=product_sku))

    if storage not in STORAGE_MULTIPLIERS:
        flash('Invalid storage option.', 'danger')
        return redirect(url_for('product_detail', product_sku=product_sku))

    # Calculate price
    multiplier = STORAGE_MULTIPLIERS[storage]
    unit_price = float(product['base_price'] * multiplier)
    item_total_price = float(unit_price * quantity)

    cart_key = f"{product_sku}-{storage}"

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # Add or update item in cart
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
        cart[cart_key]['total_price'] = float(cart[cart_key]['total_price']) + item_total_price
        flash(f'Increased quantity of {product["name"]} ({storage}) in cart.', 'info')
    else:
        cart[cart_key] = {
            'sku': product_sku,
            'name': product['name'],
            'storage': storage,
            'unit_price': unit_price,
            'quantity': quantity,
            'image': product.get('image', 'images/placeholder-phone.jpg'),
            'total_price': item_total_price
        }
        flash(f'Added {product["name"]} ({storage}) to cart.', 'success')

    session.modified = True
    return redirect(url_for('cart'))


@app.route('/cart/remove/<string:cart_key>', methods=['POST'])
@login_required
def remove_from_cart(cart_key):
    """Removes a specific item configuration from the session-based cart."""
    if 'cart' not in session or cart_key not in session['cart']:
        flash('Item not found in cart.', 'danger')
        return redirect(url_for('cart'))

    item_name = session['cart'][cart_key].get('name', 'Item')
    item_storage = session['cart'][cart_key].get('storage', '')

    del session['cart'][cart_key]
    session.modified = True

    flash(f'Removed {item_name} ({item_storage}) from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart_quantity():
    """
    Updates the quantity of all items submitted via the cart form.
    """
    if 'cart' not in session:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('cart'))

    cart = session['cart']
    updated_items = 0

    for form_key, quantity_str in request.form.items():
        if form_key.startswith('quantity-'):
            cart_key = form_key.replace('quantity-', '')
            if cart_key in cart:
                try:
                    new_quantity = int(quantity_str)
                    if new_quantity <= 0:
                        del cart[cart_key]
                        updated_items += 1
                        continue

                    current_item = cart[cart_key]
                    unit_price = float(current_item.get('unit_price', 0.0))
                    current_item['quantity'] = new_quantity
                    current_item['total_price'] = unit_price * new_quantity
                    updated_items += 1
                except ValueError:
                    flash(f"Invalid quantity submitted for item {cart_key}.", 'warning')
                except TypeError as e:
                    logging.error(f"Cart update TypeError: {e} for item {cart_key}")
                    flash(f"Data error for item {cart_key}. Price calculation failed.", 'danger')
                    continue

    if updated_items > 0 or 'cart' not in session:
        session.modified = True
        flash(f'Cart updated successfully. {updated_items} item(s) modified.', 'success')
    else:
        flash('No changes detected in cart quantities.', 'info')

    return redirect(url_for('cart'))


@app.route('/cart')
@login_required
def cart():
    # Total price variable for cart.html is provided by inject_cart context processor
    return render_template('cart.html')


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart = session.get('cart', {})
        if not cart:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('cart'))

        total_amount = 0
        transaction_items = []

        for key, item in cart.items():
            total_item_price = item['quantity'] * item['unit_price']
            total_amount += total_item_price
            transaction_items.append({
                'sku': item['sku'],
                'name': item['name'],
                'storage': item.get('storage', ''),
                'unit_price': item['unit_price'],
                'quantity': item['quantity'],
                'total_price': total_item_price
            })

        transaction_id = str(uuid.uuid4())
        new_tx = Transaction(
            transaction_id=transaction_id,
            user_id=session['user_id'],
            skus=','.join([i['sku'] for i in transaction_items]),
            items=json.dumps(transaction_items),
            total_price=total_amount,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_tx)
        db.session.commit()

        # Add to blockchain
        blockchain.new_transaction(
            sender=session['user_id'],
            recipient='Store',
            amount=total_amount,
            items=transaction_items
        )
        last_proof = blockchain.last_block['proof']
        proof = blockchain.proof_of_work(last_proof)
        blockchain.new_block(proof)

        # Clear cart
        session['cart'] = {}
        session.modified = True
        flash("Payment successful! Your order has been recorded.", "success")
        return redirect(url_for('checkout_success', transaction_id=transaction_id))

    # GET request fallback
    flash("You cannot access checkout directly.", "warning")
    return redirect(url_for('cart'))

@app.route('/checkout/success/<transaction_id>')
@login_required
def checkout_success(transaction_id):
    session['checkout_success'] = True
    tx = Transaction.query.filter_by(transaction_id=transaction_id).first()
    cart = json.loads(tx.items) if tx else []
    total_price = tx.total_price if tx else 0
    return render_template('checkout.html', cart={i['sku']: i for i in cart}, total_price=total_price)



@app.route('/ledger')
def ledger():
    # Blockchain stats
    stats = blockchain.get_blockchain_stats()
    return render_template(
        'ledger.html',
        chain=blockchain.chain,
        length=len(blockchain.chain),
        total_transactions=stats['total_transactions'],
        total_volume=stats['total_volume'],
        average_transactions_per_block=stats['average_transactions_per_block']
    )

@app.template_filter('datetimeformat')
def datetimeformat(value):
    """
    Convert Unix timestamp to human-readable format.
    """
    try:
        return datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return value


@app.route('/ai-dashboard')
@admin_required # Use the decorator for cleaner code
def ai_dashboard():
    # Fetch all products from the database
    products = Product.query.all()
    return render_template('ai_dashboard.html', title="AI Dashboard", products=products)

# ---------------- AI Prediction Endpoints ----------------

@app.route('/predict_sales', methods=['GET'])
def predict_sales_simple():
    """
    Handles simple GET requests from product cards/slideshow.
    """
    if not sales_model or not le_product or not le_series:
        return jsonify({'prediction': 'N/A', 'error': 'Model not available'}), 200

    # Get data from URL query parameters (expected by your JS)
    product_name = request.args.get('name')
    series = request.args.get('series')
    price_str = request.args.get('price')

    if not all([product_name, series, price_str]):
        return jsonify({'prediction': 'N/A', 'error': 'Missing GET parameters'}), 400

    try:
        price = float(price_str)
        # Use placeholder values for features not available on the product card
        rating = 4.0 		# Placeholder: Assume average rating
        reviews_count = 50 	# Placeholder: Assume moderate review count
        stock = 10 		# Placeholder: Assume decent stock
        
        # Encoding must handle unseen labels gracefully, but assuming product and series 
        # are known to the encoders for now. Using .transform() which raises a ValueError
        # if an unknown label is encountered.
        prod_enc = le_product.transform([product_name])[0]
        series_enc = le_series.transform([series])[0]

        X = np.array([[
            prod_enc,
            series_enc,
            price,
            rating,
            reviews_count,
            stock
        ]])
        
        prediction = sales_model.predict(X)[0]
        # Prediction must be non-negative
        predicted_sales = max(0, float(prediction))
        
        return jsonify({'prediction': round(predicted_sales, 2)}), 200
    except ValueError as e:
        # Catch value errors from float conversion or le.transform for unknown labels
        return jsonify({'prediction': 'N/A', 'error': f'Invalid data format or unknown product/series: {str(e)}'}), 400
    except Exception as e:
        # Catch other prediction failures
        return jsonify({'prediction': 'N/A', 'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/api/predict_sales', methods=['POST'])
def api_predict_sales():
    """
    Backend API for detailed Admin/AI Dashboard prediction.
    Uses the modern SalesPredictor class to handle feature engineering.
    """
    # sales_predictor instance should be initialized and accessible here
    # Check if the core predictor is trained
    if not sales_predictor.is_trained:
        # Optionally trigger training if not trained, or return an error
        sales_predictor.train() 
        if not sales_predictor.is_trained:
             return jsonify({'error': 'Sales model failed to initialize or train'}), 500

    data = request.get_json()

    # The SalesPredictor expects 'product_name', 'category', 'price', and 'date'.
    # Note: 'series' from the frontend maps to 'category' in the model.
    required_fields = ['product_name', 'series', 'price'] 
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required parameters: product_name, series (category), and price'}), 400

    try:
        # 1. Prepare Inputs for SalesPredictor
        product_name = data['product_name']
        category = data['series'] 
        price = float(data['price'])
        
        # 2. Get the date for prediction (We'll predict for today)
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # 3. Call the SalesPredictor's method
        predicted_sales_int = sales_predictor.predict_sales(
            product_name=product_name,
            category=category,
            price=price,
            date=today_date
        )
        
        # 4. Return the result
        return jsonify({'predicted_sales': float(predicted_sales_int)}), 200
        
    except Exception as e:
        # In a real app, you might log the full traceback here.
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

# ---------------- API: Cart Transactions ----------------
@app.route('/api/cart_add', methods=['POST'])
@login_required
def api_cart_add():
    """
    Saves the current session cart as a pending Transaction in the DB.
    """
    cart_data = session.get('cart', {})
    if not cart_data:
        return jsonify({'error': 'Cart is empty'}), 400

    items_list = list(cart_data.values())
    total_amount = sum(float(item.get('total_price', 0.0)) for item in items_list) # Ensure float conversion
    sender = session.get('username')
    recipient = 'ShopLess'

    # Save as pending transaction
    tx = Transaction(sender=sender, recipient=recipient, amount=total_amount, 
                     items=json.dumps(items_list), status='Pending')
    db.session.add(tx)
    db.session.commit()
    
    # Clear the session cart now that it's a pending transaction
    session.pop('cart', None)
    session.modified = True 

    return jsonify({'message': 'Items confirmed and saved as pending transaction', 'tx_id': tx.id}), 201

@app.route('/api/checkout', methods=['POST'])
@login_required
def api_checkout():
    """
    Mark pending transactions as Paid on checkout.
    """
    data = request.get_json()
    tx_id = data.get('tx_id')
    
    if tx_id:
        tx = Transaction.query.get(tx_id)
    else:
        # Fallback to look for latest pending transaction for this user
        tx = Transaction.query.filter_by(sender=session.get('username'), status='Pending').order_by(Transaction.timestamp.desc()).first()
    
    if tx and tx.status == 'Pending':
        tx.status = 'Paid'
        # Log to the blockchain after confirming payment (optional)
        try:
            items_list = json.loads(tx.items)
            blockchain.new_transaction(tx.sender, tx.recipient, tx.amount, items_list)
        except Exception as e:
            logging.error(f"Failed to record transaction to blockchain: {e}")

        db.session.commit()
        
        flash('Checkout successful! Transaction marked as Paid.', 'success')
        return jsonify({'message': 'Transaction marked as Paid'}), 200
    
    return jsonify({'error': 'Invalid or already paid transaction'}), 400


# ---------------- Admin Panel ----------------
@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin_panel.html', users=users, products=products)

@app.route('/transactions')
@admin_required
def view_transactions():
    txs = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    tx_list = []

    for t in txs:
        # Load items JSON safely
        try:
            items = json.loads(t.items)
        except Exception:
            items = []

        # Ensure each item has the keys we need
        formatted_items = []
        for item in items:
            formatted_items.append({
                'name': item.get('name', 'Unknown'),
                'sku': item.get('sku', 'N/A'),
                'quantity': item.get('quantity', 0),
                'unit_price': item.get('unit_price', 0),
                'total_price': item.get('total_price', 0)
            })

        tx_list.append({
            'transaction_id': t.transaction_id,
            'user_id': t.user_id,          # Correct field
            'items': formatted_items,
            'total_price': t.total_price,  # Correct field
            'timestamp': t.timestamp
        })

    return render_template('transactions.html', transactions=tx_list)



@app.route('/blockchain_ledger')
@admin_required
def blockchain_ledger():
    return render_template(
        'blockchain_ledger.html',
        chain=blockchain.chain,
        length=len(blockchain.chain),
        valid=blockchain.valid_chain(blockchain.chain) if hasattr(blockchain, 'valid_chain') else True
    )

# ---------------- User Auth ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '')
        role = request.form.get('role', 'Customer')

        if not username or not password:
            flash('Username and password required', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username exists', 'warning')
            return render_template('register.html')
        if email and User.query.filter_by(email=email).first():
            flash('Email exists', 'warning')
            return render_template('register.html')

        if role not in ['Customer', 'Admin']:
            role = 'Customer'

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed, role=role)
        db.session.add(user)
        db.session.commit()
        flash(f'Registered as {role}', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('home'))

# ---------------- Product Management ----------------
@app.route('/product/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        sku = request.form.get('sku', '').strip() or None
        name = request.form.get('name', '').strip()
        series = request.form.get('series', '').strip() or None
        description = request.form.get('description', '').strip() or None
        base_price = request.form.get('base_price', '0').strip()
        image = request.form.get('image', '').strip() or None
        try:
            base_price_f = float(base_price)
        except ValueError:
            flash('Invalid base price', 'danger')
            return render_template('add_product.html')
        image_path = f"images/{image}" if image and not image.startswith('images/') else image
        product = Product(sku=sku, name=name, series=series, description=description,
                          base_price=base_price_f, image=image_path)
        db.session.add(product)
        db.session.commit()
        flash('Product added', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('add_product.html')

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required  # keep login required
def edit_product(product_id):
    user_role = session.get('role')

    # Check if the current user has permission to edit products
    if not SecurityConfig.check_permission(user_role, 'edit', 'product'):
        flash('You do not have permission to edit products.', 'danger')
        return redirect(url_for('home'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.sku = request.form.get('sku', product.sku)
        product.name = request.form.get('name', product.name)
        product.series = request.form.get('series', product.series)
        product.description = request.form.get('description', product.description)
        base_price = request.form.get('base_price', product.base_price)
        image = request.form.get('image', product.image)

        try:
            product.base_price = float(base_price)
        except ValueError:
            flash('Invalid base price', 'danger')
            return render_template('edit_product.html', product=product)

        if image and not image.startswith('images/'):
            product.image = f"images/{image}"
        else:
            product.image = image

        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('edit_product.html', product=product)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'info')
    return redirect(url_for('admin_panel'))

# ---------------- Sync Hardcoded Products ----------------
def sync_products_initial():
    """Performs the initial product sync when the DB is empty."""
    added_count = 0
    for data in PRODUCT_CATALOG:
        sku = data['sku']
        image_filename = data['image']
        image_path = f"images/{image_filename}" if image_filename and not image_filename.startswith('images/') else image_filename
        
        new_product = Product(sku=sku, name=data['name'], series=data['series'],
                              description=f"iPhone {data['series']} Series",
                              base_price=data['base_price'], image=image_path)
        db.session.add(new_product)
        added_count += 1
    db.session.commit()
    print(f"Initial sync complete: {added_count} products added.")

@app.route('/admin/sync_products', methods=['POST'])
@admin_required
def sync_products():
    added_count = 0
    updated_count = 0
    for data in PRODUCT_CATALOG:
        sku = data['sku']
        product = Product.query.filter_by(sku=sku).first()
        image_filename = data['image']
        image_path = f"images/{image_filename}" if image_filename and not image_filename.startswith('images/') else image_filename
        if product:
            product.name = data['name']
            product.series = data['series']
            product.base_price = data['base_price']
            product.image = image_path
            updated_count += 1
        else:
            new_product = Product(sku=sku, name=data['name'], series=data['series'],
                                  description=f"iPhone {data['series']} Series",
                                  base_price=data['base_price'], image=image_path)
            db.session.add(new_product)
            added_count += 1
    db.session.commit()
    flash(f'Sync complete: {added_count} added, {updated_count} updated.', 'success')
    return redirect(url_for('admin_panel'))

# ---------------- Blockchain APIs ----------------
@app.route('/api/transact', methods=['POST'])
@login_required
def api_transact():
    """Records a transaction to blockchain and SQL (same as cart)."""
    try:
        data = request.get_json()
        sender = data.get('sender', session.get('username', 'Anonymous'))
        recipient = data.get('recipient', 'ShopLess')
        amount = float(data.get('amount', 0))
        items = data.get('items', [])
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        # Check if the blockchain object is initialized before using it
        if not 'blockchain' in globals() or not blockchain:
            raise Exception("Blockchain module not loaded.")

        block_index = blockchain.new_transaction(sender, recipient, amount, items)
        tx = Transaction(sender=sender, recipient=recipient, amount=amount, items=json.dumps(items), status='Paid')
        db.session.add(tx)
        db.session.commit()
        return jsonify({'message': f'Transaction recorded. Pending mining in block {block_index}',
                        'pending_index': block_index, 'sql_tx_id': tx.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mine', methods=['GET'])
@login_required
def api_mine():
    if not 'blockchain' in globals() or not blockchain:
        return jsonify({'error': 'Blockchain module not loaded.'}), 500

    if not blockchain.current_transactions:
        return jsonify({'message': 'No pending transactions to mine.'}), 200
    try:
        last_block = blockchain.last_block
        proof = blockchain.proof_of_work(last_block['proof'])
        previous_hash = blockchain.hash(last_block)
        new_block = blockchain.new_block(proof, previous_hash)
        return jsonify({'message': 'Block mined', 'index': new_block['index'],
                        'transactions_count': len(new_block['transactions'])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chain')
def api_chain():
    if not 'blockchain' in globals() or not blockchain:
        return jsonify({'error': 'Blockchain module not loaded.'}), 500
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

# ---------------- Profile & Utilities ----------------
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id']) 
    return render_template('profile.html', user=user)

@app.route('/api/products')
def api_products():
    products = Product.query.order_by(Product.name.asc()).all()
    data = [{'id': p.id, 'sku': p.sku, 'name': p.name, 'series': p.series,
             'description': p.description, 'base_price': p.base_price, 'image': p.image} for p in products]
    return jsonify(data), 200

# ---------------- Error Handlers ----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ---------------- Run App (Consolidated) ----------------
if __name__ == '__main__':
    with app.app_context():
        db_file = 'shopless.db'
        needs_init = not os.path.exists(db_file)
        db.create_all()

        if needs_init:
            print("Initializing database with default admin and sample products...")
            # Create default admin
            if not User.query.filter_by(username='admin').first():
                admin_pw = generate_password_hash('admin123')
                admin = User(username='admin', email='admin@shopless.com', password=admin_pw, role='Admin')
                db.session.add(admin)
                db.session.commit()
                print("Default Admin 'admin' created.")
            
            # Add sample products
            if Product.query.count() == 0 and PRODUCT_CATALOG:
                sync_products_initial()
            else:
                print("Products already exist in DB.")
        else:
            print("Database already exists. Skipping initial sync.")
            
    app.run(host='0.0.0.0', port=5000, debug=True)