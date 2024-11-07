from app import app, db
from models import Category, Product, User
from werkzeug.security import generate_password_hash

def initialize_sample_data():
    """Initialize sample data if the database is empty"""
    with app.app_context():
        if not Category.query.first():
            # Create sample categories
            categories = [
                Category(name='Laptops'),
                Category(name='Smartphones'),
                Category(name='Accessories'),
                Category(name='Audio'),
            ]
            for category in categories:
                db.session.add(category)
            db.session.commit()

            # Create sample products
            products = [
                {
                    'name': 'Ultra Book Pro',
                    'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
                    'price': 999.99,
                    'stock': 10,
                    'image_url': '/static/images/laptop.svg',
                    'category_id': 1,
                    'specifications': {
                        'CPU': 'Intel i7',
                        'RAM': '16GB',
                        'Storage': '512GB SSD'
                    }
                },
                {
                    'name': 'SmartPhone X',
                    'description': 'Latest smartphone with 5G capability',
                    'price': 699.99,
                    'stock': 15,
                    'image_url': '/static/images/phone.svg',
                    'category_id': 2,
                    'specifications': {
                        'Screen': '6.5 inch OLED',
                        'Camera': '48MP',
                        'Battery': '4500mAh'
                    }
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            db.session.commit()

def create_admin_user():
    '''Create admin user if it doesn't exist'''
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == "__main__":
    initialize_sample_data()
    create_admin_user()
    app.run(host="0.0.0.0", port=5000, debug=True)
