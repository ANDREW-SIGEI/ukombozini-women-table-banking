import json
from datetime import datetime
from app.models import Group, GroupMembership, User

def test_create_group(client, test_admin):
    """Test group creation"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create group
    response = client.post('/groups/create',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Test Group',
            'description': 'A test group',
            'location': 'Test Location',
            'meeting_day': 'Monday',
            'meeting_time': '14:00'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Group'
    assert data['status'] == 'active'

def test_update_group(client, test_admin, test_group):
    """Test group update"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Update group
    response = client.put(f'/groups/{test_group.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Updated Group Name',
            'description': 'Updated description'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Group Name'
    assert data['description'] == 'Updated description'

def test_add_member(client, test_admin, test_group, test_user):
    """Test adding member to group"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Add member
    response = client.post(f'/groups/{test_group.id}/members',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'user_id': test_user.id,
            'role': 'member'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user_id'] == test_user.id
    assert data['role'] == 'member'

def test_remove_member(client, test_admin, test_group, test_user):
    """Test removing member from group"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # First add member
    membership = GroupMembership(
        group_id=test_group.id,
        user_id=test_user.id,
        role='member'
    )
    db.session.add(membership)
    db.session.commit()
    
    # Remove member
    response = client.delete(f'/groups/{test_group.id}/members/{test_user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_group_statistics(client, test_admin, test_group):
    """Test group statistics"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Add some members
    members = []
    for i in range(3):
        user = User(
            email=f'member{i}@example.com',
            password='password123',
            first_name=f'Member{i}',
            last_name='Test'
        )
        db.session.add(user)
        db.session.commit()
        
        membership = GroupMembership(
            group_id=test_group.id,
            user_id=user.id,
            role='member'
        )
        members.append(membership)
    
    db.session.add_all(members)
    db.session.commit()
    
    # Get statistics
    response = client.get(f'/groups/{test_group.id}/statistics',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_members'] == 3
    assert 'total_savings' in data
    assert 'total_loans' in data

def test_group_roles(client, test_admin, test_group, test_user):
    """Test group role management"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Add member with role
    response = client.post(f'/groups/{test_group.id}/members',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'user_id': test_user.id,
            'role': 'treasurer'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['role'] == 'treasurer'
    
    # Update role
    response = client.put(f'/groups/{test_group.id}/members/{test_user.id}/role',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'role': 'secretary'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['role'] == 'secretary'

def test_group_search(client, test_admin):
    """Test group search functionality"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create test groups
    groups = [
        Group(
            name='Farmers Group',
            description='Group for farmers',
            location='Rural Area'
        ),
        Group(
            name='Business Group',
            description='Group for business owners',
            location='Urban Area'
        )
    ]
    db.session.add_all(groups)
    db.session.commit()
    
    # Search by name
    response = client.get('/groups/search',
        headers={'Authorization': f'Bearer {token}'},
        query_string={'query': 'Farmers'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['groups']) == 1
    assert data['groups'][0]['name'] == 'Farmers Group'

def test_group_activities(client, test_admin, test_group):
    """Test group activities log"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create some activities
    response = client.post(f'/groups/{test_group.id}/activities',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'activity_type': 'meeting',
            'description': 'Monthly meeting held',
            'date': datetime.now().isoformat()
        }
    )
    assert response.status_code == 201
    
    # Get activities
    response = client.get(f'/groups/{test_group.id}/activities',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['activities']) > 0 