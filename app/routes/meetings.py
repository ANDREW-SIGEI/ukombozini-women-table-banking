from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Meeting, MeetingAttendance, Group, GroupMembership, User
from app import db
from datetime import datetime, timedelta
from app.utils.auth import group_role_required
from app.utils.notifications import send_meeting_notification

bp = Blueprint('meetings', __name__)

@bp.route('/meetings', methods=['GET'])
@login_required
def get_meetings():
    """Get list of meetings with optional filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filter by group if provided
    group_id = request.args.get('group_id', type=int)
    query = Meeting.query
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    # Filter by date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        query = query.filter(Meeting.meeting_date.between(start_date, end_date))
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    return jsonify(Meeting.to_collection_dict(query, page, per_page, 'meetings.get_meetings'))

@bp.route('/meetings', methods=['POST'])
@login_required
@group_role_required(['chairperson', 'secretary'])
def create_meeting():
    """Create a new meeting"""
    data = request.get_json()
    
    # Validate meeting date is in the future
    meeting_date = datetime.strptime(data['meeting_date'], '%Y-%m-%d %H:%M')
    if meeting_date <= datetime.now():
        return jsonify({'error': 'Meeting date must be in the future'}), 400
    
    meeting = Meeting(
        group_id=data['group_id'],
        title=data['title'],
        description=data.get('description'),
        meeting_date=meeting_date,
        location=data['location'],
        meeting_type=data.get('meeting_type', 'regular'),
        duration=data.get('duration', 60),  # Default 60 minutes
        status='scheduled',
        agenda=data.get('agenda'),
        created_by=current_user.id
    )
    
    db.session.add(meeting)
    db.session.commit()
    
    # Send notifications to group members
    send_meeting_notification(meeting, 'scheduled')
    
    return jsonify(meeting.to_dict()), 201

@bp.route('/meetings/<int:id>', methods=['GET'])
@login_required
def get_meeting(id):
    """Get meeting details"""
    meeting = Meeting.query.get_or_404(id)
    return jsonify(meeting.to_dict())

@bp.route('/meetings/<int:id>', methods=['PUT'])
@login_required
@group_role_required(['chairperson', 'secretary'])
def update_meeting(id):
    """Update meeting details"""
    meeting = Meeting.query.get_or_404(id)
    data = request.get_json()
    
    # Check if meeting is being rescheduled
    if 'meeting_date' in data:
        new_date = datetime.strptime(data['meeting_date'], '%Y-%m-%d %H:%M')
        if new_date != meeting.meeting_date:
            meeting.meeting_date = new_date
            meeting.status = 'rescheduled'
            # Send reschedule notification
            send_meeting_notification(meeting, 'rescheduled', data.get('reason'))
    
    meeting.title = data.get('title', meeting.title)
    meeting.description = data.get('description', meeting.description)
    meeting.location = data.get('location', meeting.location)
    meeting.meeting_type = data.get('meeting_type', meeting.meeting_type)
    meeting.duration = data.get('duration', meeting.duration)
    meeting.agenda = data.get('agenda', meeting.agenda)
    
    db.session.commit()
    return jsonify(meeting.to_dict())

@bp.route('/meetings/<int:id>/cancel', methods=['POST'])
@login_required
@group_role_required(['chairperson', 'secretary'])
def cancel_meeting(id):
    """Cancel a meeting"""
    meeting = Meeting.query.get_or_404(id)
    data = request.get_json()
    
    meeting.status = 'cancelled'
    meeting.cancellation_reason = data.get('reason')
    meeting.cancelled_by = current_user.id
    meeting.cancelled_at = datetime.utcnow()
    
    db.session.commit()
    
    # Send cancellation notification
    send_meeting_notification(meeting, 'cancelled', data.get('reason'))
    
    return jsonify(meeting.to_dict())

@bp.route('/meetings/<int:id>/attendance', methods=['POST'])
@login_required
def record_attendance(id):
    """Record meeting attendance"""
    meeting = Meeting.query.get_or_404(id)
    data = request.get_json()
    
    attendance = MeetingAttendance(
        meeting_id=id,
        user_id=data['user_id'],
        status=data['status'],  # present, absent, excused
        notes=data.get('notes')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 201

@bp.route('/meetings/stats', methods=['GET'])
@login_required
def get_meeting_stats():
    """Get meeting statistics"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get upcoming meetings (next 7 days)
    upcoming_meetings = Meeting.query.filter(
        Meeting.meeting_date > datetime.now(),
        Meeting.meeting_date <= datetime.now() + timedelta(days=7),
        Meeting.status == 'scheduled'
    ).count()
    
    # Get today's meetings
    today_meetings = Meeting.query.filter(
        Meeting.meeting_date >= datetime.combine(today, datetime.min.time()),
        Meeting.meeting_date < datetime.combine(tomorrow, datetime.min.time()),
        Meeting.status == 'scheduled'
    ).count()
    
    # Calculate average attendance
    total_meetings = Meeting.query.filter_by(status='completed').count()
    if total_meetings > 0:
        total_attendance = MeetingAttendance.query.filter_by(status='present').count()
        avg_attendance = (total_attendance / (total_meetings * 10)) * 100  # Assuming 10 members per meeting
    else:
        avg_attendance = 0
    
    return jsonify({
        'upcoming_meetings': upcoming_meetings,
        'today_meetings': today_meetings,
        'avg_attendance': round(avg_attendance, 1)
    })

@bp.route('/meetings/upcoming', methods=['GET'])
@login_required
def get_upcoming_meetings():
    """Get upcoming meetings for the current user"""
    # Get groups where user is a member
    user_groups = GroupMembership.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).all()
    group_ids = [membership.group_id for membership in user_groups]
    
    # Get upcoming meetings for these groups
    meetings = Meeting.query.filter(
        Meeting.group_id.in_(group_ids),
        Meeting.meeting_date > datetime.now(),
        Meeting.status == 'scheduled'
    ).order_by(Meeting.meeting_date).limit(5).all()
    
    return jsonify({
        'meetings': [meeting.to_dict() for meeting in meetings]
    }) 