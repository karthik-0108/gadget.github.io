from flask import render_template, request, jsonify, redirect, url_for, flash, abort
from app import app, db, mail
from models import Product, Category, Order, OrderItem, User
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Message

@app.route('/')
def home():
    featured_products = Product.query.limit(6).all()
    categories = Category.query.all()
    return render_template('home.html', products=featured_products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/dashboard.html')

@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        
        if not all([name, description, price, stock, category_id]):
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('admin_products'))
        
        try:
            product = Product(
                name=name,
                description=description,
                price=float(price),
                stock=int(stock),
                category_id=int(category_id)
            )
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except ValueError:
            flash('Invalid input values', 'danger')
        return redirect(url_for('admin_products'))
        
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        abort(403)
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/products')
def products():
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('q')
    
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    products = query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400
        
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock'}), 400
    
    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url
        }
    })

def send_order_confirmation(order):
    try:
        msg = Message(
            subject='Order Confirmation - Electronics Store',
            sender=app.config['MAIL_USERNAME'],
            recipients=[order.user.email]
        )
        msg.html = render_template('email/order_confirmation.html', order=order)
        
        try:
            mail.send(msg)
            return True
        except Exception as e:
            app.logger.error(f'Failed to send confirmation email: {str(e)}')
            if 'BadCredentials' in str(e):
                flash('Order placed successfully. Email notifications are temporarily unavailable.', 'warning')
            return False
            
    except Exception as e:
        app.logger.error(f'Error preparing confirmation email: {str(e)}')
        return False

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        try:
            data = request.get_json()
            cart_items = data.get('cart_items', [])
            shipping_info = data.get('shipping_info', {})

            if not cart_items:
                return jsonify({'error': 'Cart is empty'}), 400
            
            if not shipping_info or not all(shipping_info.values()):
                return jsonify({'error': 'Shipping information is incomplete'}), 400

            # Calculate total amount
            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
            shipping_cost = 10
            total_amount += shipping_cost

            # Create order record
            order = Order(
                user_id=current_user.id,
                total_amount=total_amount,
                status='paid'  # Mark as paid for development
            )
            db.session.add(order)
            db.session.flush()  # Get order ID without committing
            
            # Create order items
            for item in cart_items:
                product = Product.query.get(item['id'])
                if not product:
                    db.session.rollback()
                    return jsonify({'error': f'Product {item["id"]} not found'}), 400
                
                if product.stock < item['quantity']:
                    db.session.rollback()
                    return jsonify({'error': f'Insufficient stock for {product.name}'}), 400

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_item)
                
                # Update product stock
                product.stock -= item['quantity']

            db.session.commit()
            
            # Send confirmation email with fallback
            email_sent = send_order_confirmation(order)
            if not email_sent:
                flash('Order placed successfully but confirmation email could not be sent.', 'warning')
            
            return jsonify({
                'success': True,
                'redirect': url_for('order_success')
            })

        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Order creation error: {str(e)}')
            return jsonify({'error': 'Failed to process order. Please try again.'}), 500

    return render_template('checkout.html')

@app.route('/order/success')
@login_required
def order_success():
    # Get the latest order for the current user
    order = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).first()
    if not order:
        abort(404)
    return render_template('order_success.html', order=order)

@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
