from app import db
from datetime import datetime

class VisitReport(db.Model):
    __tablename__ = 'visit_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    meeting_held = db.Column(db.Boolean, default=True)
    attendance_percentage = db.Column(db.Integer, default=0)  # 0-100
    status = db.Column(db.String(20), default='pending')  # pending, completed
    report_content = db.Column(db.Text, nullable=False)
    challenges = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - changed backref name to individual_visit_reports to avoid conflicts
    officer = db.relationship('User', backref=db.backref('individual_visit_reports', lazy='dynamic'))
    group = db.relationship('Group', backref=db.backref('individual_visit_reports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<VisitReport {self.id} - {self.visit_date}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'officer_id': self.officer_id,
            'group_id': self.group_id,
            'visit_date': self.visit_date.strftime('%Y-%m-%d') if self.visit_date else None,
            'meeting_held': self.meeting_held,
            'attendance_percentage': self.attendance_percentage,
            'status': self.status,
            'report_content': self.report_content,
            'challenges': self.challenges,
            'recommendations': self.recommendations,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 