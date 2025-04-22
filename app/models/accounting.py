from app import db
from .base import Model, TimestampMixin, PaginatedAPIMixin
from datetime import datetime

class AccountingTransaction(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'accounting_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense, transfer
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(256))
    category = db.Column(db.String(64), nullable=False)  # e.g., loan_payment, salary, utilities
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    reference_number = db.Column(db.String(64))
    payment_method = db.Column(db.String(20))  # cash, bank_transfer, mobile_money
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    notes = db.Column(db.Text)
    
    # Optional foreign keys for related entities
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    
    def __repr__(self):
        return f'<AccountingTransaction {self.id} - {self.transaction_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'description': self.description,
            'category': self.category,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'reference_number': self.reference_number,
            'payment_method': self.payment_method,
            'status': self.status,
            'notes': self.notes,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DividendDistribution(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'dividend_distributions'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    distribution_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed
    distribution_type = db.Column(db.String(20), nullable=False)  # annual, semi_annual, quarterly
    year = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(20))  # Q1, Q2, Q3, Q4, H1, H2
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref=db.backref('dividend_distributions', lazy='dynamic'))
    payments = db.relationship('DividendPayment', back_populates='distribution')

    def __repr__(self):
        return f'<DividendDistribution {self.id} - {self.group_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'total_amount': float(self.total_amount),
            'distribution_date': self.distribution_date.isoformat() if self.distribution_date else None,
            'status': self.status,
            'distribution_type': self.distribution_type,
            'year': self.year,
            'period': self.period,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DividendPayment(Model, TimestampMixin):
    __tablename__ = 'dividend_payments'

    id = db.Column(db.Integer, primary_key=True)
    distribution_id = db.Column(db.Integer, db.ForeignKey('dividend_distributions.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_method = db.Column(db.String(20))  # cash, bank_transfer, mobile_money
    reference_number = db.Column(db.String(64))
    notes = db.Column(db.Text)
    
    # Relationships
    distribution = db.relationship('DividendDistribution', back_populates='payments')
    user = db.relationship('User', backref=db.backref('dividend_payments', lazy='dynamic')) 