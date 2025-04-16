from app import db
from .base import Model, TimestampMixin, PaginatedAPIMixin
from datetime import datetime

class Loan(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)  # Annual interest rate
    term_months = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(256))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, active, completed, defaulted
    disbursement_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='loans')
    payments = db.relationship('LoanPayment', back_populates='loan')

    def __repr__(self):
        return f'<Loan {self.id} - {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'interest_rate': float(self.interest_rate),
            'term_months': self.term_months,
            'purpose': self.purpose,
            'status': self.status,
            'disbursement_date': self.disbursement_date.isoformat() if self.disbursement_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class GroupLoan(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'group_loans'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(256))
    status = db.Column(db.String(20), default='pending')
    disbursement_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    
    # Relationships
    group = db.relationship('Group', back_populates='loans')
    payments = db.relationship('GroupLoanPayment', back_populates='loan')

class Saving(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'savings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal
    description = db.Column(db.String(256))
    
    # Relationships
    user = db.relationship('User', back_populates='savings')

class GroupSaving(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'group_savings'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal
    description = db.Column(db.String(256))
    
    # Relationships
    group = db.relationship('Group', back_populates='savings')

class LoanPayment(Model, TimestampMixin):
    __tablename__ = 'loan_payments'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(20))  # cash, mobile_money, bank_transfer
    reference_number = db.Column(db.String(64))
    
    # Relationships
    loan = db.relationship('Loan', back_populates='payments')

class GroupLoanPayment(Model, TimestampMixin):
    __tablename__ = 'group_loan_payments'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('group_loans.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(20))
    reference_number = db.Column(db.String(64))
    
    # Relationships
    loan = db.relationship('GroupLoan', back_populates='payments')

class TableBankingAccount(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'tablebanking_accounts'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True, nullable=True)
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, closed, suspended
    last_transaction_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    member = db.relationship('User', backref='tablebanking_accounts')
    group = db.relationship('Group', backref='tablebanking_accounts')
    transactions = db.relationship('TableBankingTransaction', back_populates='account')
    
    def __repr__(self):
        return f'<TableBankingAccount {self.id} - Member: {self.member_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'group_id': self.group_id,
            'balance': float(self.balance),
            'status': self.status,
            'last_transaction_date': self.last_transaction_date.isoformat() if self.last_transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TableBankingTransaction(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'tablebanking_transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('tablebanking_accounts.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, interest
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reference_number = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.String(256), nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    account = db.relationship('TableBankingAccount', back_populates='transactions')
    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='recorded_tablebanking_transactions')
    
    def __repr__(self):
        return f'<TableBankingTransaction {self.id} - {self.transaction_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TableBankingInterest(Model, TimestampMixin):
    __tablename__ = 'tablebanking_interest'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True, nullable=True)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)  # Monthly interest rate percentage
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    distribution_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, calculated, distributed
    total_amount = db.Column(db.Numeric(12, 2), default=0.00)
    notes = db.Column(db.String(256), nullable=True)
    calculated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    group = db.relationship('Group', backref='tablebanking_interest')
    calculator = db.relationship('User', foreign_keys=[calculated_by], backref='calculated_tablebanking_interest')
    
    def __repr__(self):
        return f'<TableBankingInterest {self.id} - Rate: {self.interest_rate}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'interest_rate': float(self.interest_rate),
            'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None,
            'distribution_date': self.distribution_date.isoformat() if self.distribution_date else None,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'calculated_by': self.calculated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 