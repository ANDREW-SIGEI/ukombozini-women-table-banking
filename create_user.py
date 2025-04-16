from app import create_app, db
from app.models.user import User

app = create_app('development')

with app.app_context():
    # Check if user already exists
    if not User.query.filter_by(username='admin').first():
        # Create a new admin user
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists') 