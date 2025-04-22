import json
from flask_login import current_user
from app.models import User, Role
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'Password123!',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+254712345678'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['email'] == 'newuser@example.com'
    assert 'password' not in data
    assert data['first_name'] == 'John'

def test_user_login(client, test_user):
    """Test user login"""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_invalid_login(client):
    """Test invalid login credentials"""
    response = client.post('/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_password_reset_request(client, test_user):
    """Test password reset request"""
    response = client.post('/auth/password-reset-request', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_password_reset(client, test_user):
    """Test password reset"""
    # First request reset token
    client.post('/auth/password-reset-request', json={
        'email': 'test@example.com'
    })
    
    # Simulate having a valid reset token
    reset_token = 'simulated_reset_token'
    
    response = client.post('/auth/password-reset', json={
        'token': reset_token,
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_refresh_token(client, test_user):
    """Test token refresh"""
    # First login to get tokens
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    refresh_token = json.loads(login_response.data)['refresh_token']
    
    # Use refresh token to get new access token
    response = client.post('/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_change_password(client, test_user):
    """Test password change"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Change password
    response = client.post('/auth/change-password',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'current_password': 'password123',
            'new_password': 'NewPassword123!'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_user_profile(client, test_user):
    """Test user profile operations"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Get profile
    response = client.get('/auth/profile',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'test@example.com'
    
    # Update profile
    response = client.put('/auth/profile',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'Updated',
            'phone_number': '+254787654321'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['first_name'] == 'Updated'

def test_role_assignment(client, test_admin):
    """Test role assignment"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a new user
    user = User(
        email='roletest@example.com',
        password='password123',
        first_name='Role',
        last_name='Test'
    )
    db.session.add(user)
    db.session.commit()
    
    # Assign role
    response = client.post('/auth/assign-role',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'user_id': user.id,
            'role': 'field_officer'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'field_officer' in [role.name for role in data['roles']]

def test_logout(client, test_user):
    """Test user logout"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Logout
    response = client.post('/auth/logout',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Try to use the token after logout
    response = client.get('/auth/profile',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 401 