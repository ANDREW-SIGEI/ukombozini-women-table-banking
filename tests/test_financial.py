import json
from datetime import datetime, timedelta
from app.models import Loan, GroupLoan, Saving, GroupSaving

def test_create_loan(client, test_user):
    """Test loan creation"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create loan
    response = client.post('/financial/loans', 
        headers={'Authorization': f'Bearer {token}'},
        json={
            'amount': 10000,
            'term_months': 12,
            'interest_rate': 15.0,
            'purpose': 'Business expansion'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 10000
    assert data['status'] == 'pending'

def test_approve_loan(client, test_admin):
    """Test loan approval"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a loan
    loan = Loan(
        user_id=test_admin.id,
        amount=10000,
        term_months=12,
        interest_rate=15.0,
        status='pending'
    )
    db.session.add(loan)
    db.session.commit()
    
    # Approve loan
    response = client.post(f'/financial/loans/{loan.id}/approve',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'approved'

def test_create_saving(client, test_user):
    """Test saving creation"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create saving
    response = client.post('/financial/savings',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'amount': 5000,
            'type': 'regular'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 5000
    assert data['type'] == 'regular'

def test_create_group_loan(client, test_group, test_admin):
    """Test group loan creation"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create group loan
    response = client.post('/financial/group-loans',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'group_id': test_group.id,
            'amount': 50000,
            'term_months': 24,
            'interest_rate': 12.0,
            'purpose': 'Group project'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 50000
    assert data['status'] == 'pending'

def test_loan_repayment(client, test_user):
    """Test loan repayment"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create and approve a loan
    loan = Loan(
        user_id=test_user.id,
        amount=10000,
        term_months=12,
        interest_rate=15.0,
        status='disbursed'
    )
    db.session.add(loan)
    db.session.commit()
    
    # Make payment
    response = client.post(f'/financial/loans/{loan.id}/payments',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'amount': 1000,
            'payment_method': 'cash',
            'reference_number': 'PAY123'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['amount'] == 1000
    assert data['status'] == 'paid'

def test_calculate_loan_schedule(client, test_user):
    """Test loan schedule calculation"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Calculate schedule
    response = client.post('/financial/calculate-schedule',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'amount': 10000,
            'term_months': 12,
            'interest_rate': 15.0
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['schedule']) == 12
    assert 'payment_amount' in data['schedule'][0]
    assert 'principal' in data['schedule'][0]
    assert 'interest' in data['schedule'][0]

def test_loan_overdue(client, test_user):
    """Test loan overdue detection"""
    # Create an overdue loan
    loan = Loan(
        user_id=test_user.id,
        amount=10000,
        term_months=12,
        interest_rate=15.0,
        status='disbursed',
        due_date=datetime.now() - timedelta(days=10)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Check loan status
    response = client.get(f'/financial/loans/{loan.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['is_overdue'] == True
    assert 'late_fees' in data

def test_group_saving(client, test_group, test_user):
    """Test group saving operations"""
    # First login
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create group saving
    response = client.post('/financial/group-savings',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'group_id': test_group.id,
            'amount': 20000,
            'type': 'regular'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 20000
    assert data['type'] == 'regular' 