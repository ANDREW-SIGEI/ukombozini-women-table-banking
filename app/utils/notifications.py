from flask import current_app
from app.models import Meeting, GroupMembership, User
from app import mail
from flask_mail import Message
import requests
from datetime import datetime, timedelta

def send_meeting_notification(meeting, notification_type, reason=None):
    """Send meeting notifications to group members"""
    # Get all active group members
    members = GroupMembership.query.filter_by(
        group_id=meeting.group_id,
        status='active'
    ).all()
    
    for membership in members:
        user = User.query.get(membership.user_id)
        if not user.email and not user.phone:
            continue
            
        # Prepare notification content
        subject = f"Meeting {notification_type.title()}: {meeting.title}"
        body = f"""
        Dear {user.username},
        
        This is to inform you that the meeting "{meeting.title}" has been {notification_type}.
        
        Meeting Details:
        - Date: {meeting.meeting_date.strftime('%B %d, %Y %I:%M %p')}
        - Location: {meeting.location}
        - Type: {meeting.meeting_type.title()}
        - Duration: {meeting.duration} minutes
        """
        
        if reason:
            body += f"\nReason: {reason}\n"
            
        if notification_type == 'scheduled':
            body += "\nPlease mark your calendar and plan to attend."
        elif notification_type == 'rescheduled':
            body += "\nPlease update your calendar accordingly."
        elif notification_type == 'cancelled':
            body += "\nWe apologize for any inconvenience caused."
            
        # Send email notification
        if user.email:
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            mail.send(msg)
            
        # Send SMS notification
        if user.phone:
            send_sms(user.phone, body)

def send_sms(phone_number, message):
    """Send SMS using configured SMS gateway"""
    sms_gateway = current_app.config.get('SMS_GATEWAY')
    api_key = current_app.config.get('SMS_API_KEY')
    
    if not sms_gateway or not api_key:
        current_app.logger.warning("SMS gateway not configured")
        return
        
    try:
        response = requests.post(
            sms_gateway,
            json={
                'to': phone_number,
                'message': message,
                'api_key': api_key
            }
        )
        response.raise_for_status()
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")

def send_meeting_reminders():
    """Send reminders for upcoming meetings"""
    # Get meetings happening in the next 24 hours
    upcoming_meetings = Meeting.query.filter(
        Meeting.meeting_date > datetime.now(),
        Meeting.meeting_date <= datetime.now() + timedelta(days=1),
        Meeting.status == 'scheduled'
    ).all()
    
    for meeting in upcoming_meetings:
        send_meeting_notification(meeting, 'reminder') 