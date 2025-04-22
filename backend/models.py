# Save this as models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, text

db = SQLAlchemy()

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(20), unique=True, nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    county = db.Column(db.String(50), nullable=False)
    sub_county = db.Column(db.String(50), nullable=False)
    constituency = db.Column(db.String(50), nullable=False)
    ward = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    sub_location = db.Column(db.String(50), nullable=False)
    village = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status = db.Column(db.String(20), server_default='active')
    members_count = db.Column(db.Integer, server_default=text('0'))

    __table_args__ = (
        Index('idx_county', 'county'),
        Index('idx_status', 'status'),
    )

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15))
    group_id = db.Column(db.String(20), db.ForeignKey('groups.group_id'))
    role = db.Column(db.String(20), server_default='member')
    join_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), server_default='active')
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    group = db.relationship('Group', backref='members')

    __table_args__ = (
        Index('idx_member_group', 'group_id'),
        Index('idx_national_id', 'national_id'),
    )

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(20), unique=True, nullable=False)
    member_id = db.Column(db.String(20), db.ForeignKey('members.member_id'))
    loan_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), server_default='pending')
    disbursement_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    member = db.relationship('Member', backref='loans')

    __table_args__ = (
        Index('idx_loan_status', 'status'),
        Index('idx_loan_member', 'member_id'),
    )

class LoanPayment(db.Model):
    __tablename__ = 'loan_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False)
    loan_id = db.Column(db.String(20), db.ForeignKey('loans.loan_id'))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    receipt_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    loan = db.relationship('Loan', backref='payments')

    __table_args__ = (
        Index('idx_payment_loan', 'loan_id'),
        Index('idx_payment_date', 'payment_date'),
    )

class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(20), unique=True, nullable=False)
    group_id = db.Column(db.String(20), db.ForeignKey('groups.group_id'))
    title = db.Column(db.String(200), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    meeting_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200))
    agenda = db.Column(db.Text)
    status = db.Column(db.String(20), server_default='scheduled')
    minutes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    group = db.relationship('Group', backref='meetings')

    __table_args__ = (
        Index('idx_meeting_group', 'group_id'),
        Index('idx_meeting_date', 'meeting_date'),
    )

class FieldReport(db.Model):
    __tablename__ = 'field_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(20), unique=True, nullable=False)
    officer_id = db.Column(db.String(20), nullable=False)
    group_id = db.Column(db.String(20), db.ForeignKey('groups.group_id'))
    visit_date = db.Column(db.Date, nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    findings = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text)
    status = db.Column(db.String(20), server_default='submitted')
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    group = db.relationship('Group', backref='reports')

    __table_args__ = (
        Index('idx_report_group', 'group_id'),
        Index('idx_report_officer', 'officer_id'),
        Index('idx_report_date', 'visit_date'),
    )