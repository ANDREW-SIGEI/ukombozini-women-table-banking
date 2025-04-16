import json
from datetime import datetime, timedelta
from app.models import Meeting, MeetingAttendance, Group

def test_create_meeting(client, test_admin, test_group):
    """Test meeting creation"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    meeting_date = datetime.now() + timedelta(days=7)
    # Create meeting
    response = client.post('/meetings/create',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'group_id': test_group.id,
            'title': 'Monthly Progress Review',
            'date': meeting_date.isoformat(),
            'location': 'Community Hall',
            'agenda': ['Financial Report', 'New Projects', 'AOB'],
            'duration_minutes': 120
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Monthly Progress Review'
    assert data['status'] == 'scheduled'

def test_update_meeting(client, test_admin):
    """Test meeting update"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a meeting
    meeting = Meeting(
        group_id=1,
        title='Initial Meeting',
        date=datetime.now() + timedelta(days=7),
        location='Office',
        status='scheduled'
    )
    db.session.add(meeting)
    db.session.commit()
    
    # Update meeting
    response = client.put(f'/meetings/{meeting.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Updated Meeting',
            'location': 'Conference Room'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Meeting'
    assert data['location'] == 'Conference Room'

def test_record_attendance(client, test_admin, test_group):
    """Test recording meeting attendance"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a meeting
    meeting = Meeting(
        group_id=test_group.id,
        title='Test Meeting',
        date=datetime.now(),
        location='Office',
        status='in_progress'
    )
    db.session.add(meeting)
    db.session.commit()
    
    # Record attendance
    response = client.post(f'/meetings/{meeting.id}/attendance',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'attendees': [
                {'member_id': 1, 'status': 'present'},
                {'member_id': 2, 'status': 'absent', 'reason': 'Sick'}
            ]
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['attendance']) == 2

def test_meeting_minutes(client, test_admin):
    """Test recording meeting minutes"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a meeting
    meeting = Meeting(
        group_id=1,
        title='Test Meeting',
        date=datetime.now(),
        location='Office',
        status='in_progress'
    )
    db.session.add(meeting)
    db.session.commit()
    
    # Record minutes
    response = client.post(f'/meetings/{meeting.id}/minutes',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'minutes': [
                {
                    'topic': 'Opening',
                    'discussion': 'Meeting called to order at 10:00 AM',
                    'decisions': ['Approved previous minutes']
                },
                {
                    'topic': 'Financial Report',
                    'discussion': 'Reviewed Q1 performance',
                    'decisions': ['Approved budget for Q2']
                }
            ]
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['minutes']) == 2

def test_meeting_reminders(client, test_admin, test_group):
    """Test meeting reminder functionality"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create upcoming meetings
    meetings = [
        Meeting(
            group_id=test_group.id,
            title=f'Meeting {i}',
            date=datetime.now() + timedelta(days=i),
            location='Office',
            status='scheduled'
        )
        for i in range(1, 4)
    ]
    db.session.add_all(meetings)
    db.session.commit()
    
    # Get upcoming meetings
    response = client.get('/meetings/upcoming',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['meetings']) == 3

def test_meeting_cancellation(client, test_admin):
    """Test meeting cancellation"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create a meeting
    meeting = Meeting(
        group_id=1,
        title='Test Meeting',
        date=datetime.now() + timedelta(days=1),
        location='Office',
        status='scheduled'
    )
    db.session.add(meeting)
    db.session.commit()
    
    # Cancel meeting
    response = client.post(f'/meetings/{meeting.id}/cancel',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'reason': 'Venue unavailable'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'cancelled'
    assert data['cancellation_reason'] == 'Venue unavailable'

def test_meeting_statistics(client, test_admin, test_group):
    """Test meeting statistics"""
    # First login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Create meetings with attendance
    meetings = []
    for i in range(3):
        meeting = Meeting(
            group_id=test_group.id,
            title=f'Meeting {i}',
            date=datetime.now() - timedelta(days=i*7),
            location='Office',
            status='completed'
        )
        meetings.append(meeting)
    
    db.session.add_all(meetings)
    db.session.commit()
    
    # Add attendance records
    for meeting in meetings:
        attendance = [
            MeetingAttendance(
                meeting_id=meeting.id,
                member_id=1,
                status='present'
            ),
            MeetingAttendance(
                meeting_id=meeting.id,
                member_id=2,
                status='absent'
            )
        ]
        db.session.add_all(attendance)
    db.session.commit()
    
    # Get statistics
    response = client.get(f'/meetings/statistics/{test_group.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_meetings' in data
    assert 'attendance_rate' in data
    assert 'meeting_frequency' in data 