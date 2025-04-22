from app import db
from datetime import datetime
from .base import Model, TimestampMixin

class FieldOfficerAssignment(Model, TimestampMixin):
    __tablename__ = 'field_officer_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    rotation_start_date = db.Column(db.DateTime, nullable=False)
    rotation_end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    # Relationships
    officer = db.relationship('User', backref=db.backref('assignments', lazy=True))
    group = db.relationship('Group', backref=db.backref('officer_assignments', lazy=True))
    
    def __repr__(self):
        return f'<FieldOfficerAssignment {self.officer_id} - {self.group_id}>'

class Visit(Model, TimestampMixin):
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    visit_date = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.String(256))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # scheduled, completed, cancelled
    
    # Relationships
    field_officer = db.relationship('User', backref=db.backref('visits', lazy=True))
    group = db.relationship('Group', backref=db.backref('visits', lazy=True))
    
    def __repr__(self):
        return f'<Visit {self.field_officer_id} to {self.group_id} on {self.visit_date}>'

class OfficerRotation(Model, TimestampMixin):
    __tablename__ = 'officer_rotations'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    current_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    new_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    rotation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    
    # Relationships
    field_officer = db.relationship('User', backref=db.backref('rotations', lazy=True))
    current_group = db.relationship('Group', foreign_keys=[current_group_id], backref=db.backref('outgoing_officers', lazy=True))
    new_group = db.relationship('Group', foreign_keys=[new_group_id], backref=db.backref('incoming_officers', lazy=True))
    
    def __repr__(self):
        return f'<OfficerRotation {self.field_officer_id} from {self.current_group_id} to {self.new_group_id}>'

class GroupVisitReport(db.Model):
    __tablename__ = 'group_visit_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_count = db.Column(db.Integer)
    collections_amount = db.Column(db.Numeric(10, 2))
    issues_raised = db.Column(db.Text)
    action_items = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - updated backref names to avoid conflicts with VisitReport
    officer = db.relationship('User', backref='group_visit_reports')
    group = db.relationship('Group', backref='group_visit_reports')
    visit = db.relationship('Visit', backref='report', uselist=False)
    
    def __repr__(self):
        return f'<GroupVisitReport {self.id}>'

class OfficerPerformance(db.Model):
    __tablename__ = 'officer_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    performance_score = db.Column(db.Numeric(4, 2))
    attendance_rate = db.Column(db.Numeric(5, 2))
    collection_efficiency = db.Column(db.Numeric(5, 2))
    visit_frequency = db.Column(db.Numeric(5, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    officer = db.relationship('User', backref='performance_records')
    
    def __repr__(self):
        return f'<OfficerPerformance {self.officer_id}: {self.month}/{self.year}>'

class RotationHistory(db.Model):
    __tablename__ = 'rotation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    prev_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    new_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    rotation_date = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    officer = db.relationship('User', backref='rotation_history')
    prev_group = db.relationship('Group', foreign_keys=[prev_group_id], backref='outgoing_rotations')
    new_group = db.relationship('Group', foreign_keys=[new_group_id], backref='incoming_rotations')
    
    def __repr__(self):
        return f'<RotationHistory {self.officer_id}: {self.prev_group_id} to {self.new_group_id}>'

class FieldOfficer(db.Model):
    __tablename__ = 'field_officers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    id_number = db.Column(db.String(20), unique=True)
    employment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User (optional)
    user = db.relationship('User', backref=db.backref('field_officer_profile', uselist=False))
    
    def __repr__(self):
        return f'<FieldOfficer {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" 