from app import db
from datetime import datetime

class LoanProduct(db.Model):
    __tablename__ = 'loan_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    interest_rate = db.Column(db.Float, nullable=False)
    min_amount = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    min_term = db.Column(db.Integer, nullable=False)  # in months
    max_term = db.Column(db.Integer, nullable=False)  # in months
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LoanProduct {self.name}>'

class SavingProduct(db.Model):
    __tablename__ = 'saving_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    interest_rate = db.Column(db.Float, nullable=False)
    min_balance = db.Column(db.Float, nullable=False)
    withdrawal_fee = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SavingProduct {self.name}>' 