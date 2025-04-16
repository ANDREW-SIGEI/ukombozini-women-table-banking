from datetime import datetime
from app.models.base import db

class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = db.relationship('Group', backref=db.backref('meetings', lazy=True))
    attendance = db.relationship('MeetingAttendance', backref='meeting', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Meeting {self.title}>'

class MeetingAttendance(db.Model):
    __tablename__ = 'meeting_attendance'

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('meeting_attendance', lazy=True))

    def __repr__(self):
        return f'<MeetingAttendance {self.user_id} for meeting {self.meeting_id}>' 