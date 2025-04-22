import os
from app import create_app, db
from app.models.user import User

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User
    }

@app.before_first_request
def initialize_database():
    """Initialize the database with required tables and a test admin user"""
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

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True) 