from app import create_app, db
from app.models.user import User

app = create_app('development')

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if admin user already exists
    if not User.query.filter_by(username='admin').first():
        # Create a test admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        admin.set_password('password')
        db.session.add(admin)
        
        # Create a test regular user
        user = User(
            username='user',
            email='user@example.com',
            first_name='Regular',
            last_name='User',
            role='member',
            is_active=True
        )
        user.set_password('password')
        db.session.add(user)
        
        db.session.commit()
        print("Database initialized with admin and user accounts")
    else:
        print("Admin user already exists") 