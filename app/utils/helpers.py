from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Union
from flask import current_app
import jwt
from werkzeug.security import generate_password_hash

def calculate_loan_schedule(amount: float, interest_rate: float, term_months: int) -> List[Dict[str, Any]]:
    """Calculate loan repayment schedule"""
    amount = Decimal(str(amount))
    interest_rate = Decimal(str(interest_rate))
    monthly_rate = interest_rate / Decimal('100') / Decimal('12')
    
    # Calculate monthly payment using PMT formula
    monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
    
    schedule = []
    remaining_balance = amount
    payment_date = datetime.now()
    
    for month in range(1, term_months + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'payment_number': month,
            'payment_date': payment_date.strftime('%Y-%m-%d'),
            'payment_amount': float(round(monthly_payment, 2)),
            'principal': float(round(principal_payment, 2)),
            'interest': float(round(interest_payment, 2)),
            'remaining_balance': float(round(remaining_balance, 2))
        })
        
        payment_date += timedelta(days=30)
    
    return schedule

def calculate_dividend(total_amount: float, member_shares: Dict[int, int]) -> Dict[int, float]:
    """Calculate dividend distribution based on member shares"""
    total_shares = sum(member_shares.values())
    total_amount = Decimal(str(total_amount))
    
    distribution = {}
    for member_id, shares in member_shares.items():
        share_ratio = Decimal(str(shares)) / Decimal(str(total_shares))
        distribution[member_id] = float(total_amount * share_ratio)
    
    return distribution

def generate_reference_number(prefix: str, id: int) -> str:
    """Generate a unique reference number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    return f"{prefix}-{timestamp}-{str(id).zfill(6)}"

def generate_password_reset_token(user_id: int, expires_in: int = 600) -> str:
    """Generate password reset token"""
    return jwt.encode(
        {'reset_password': user_id, 'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_password_reset_token(token: str) -> Union[int, None]:
    """Verify password reset token"""
    try:
        id = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )['reset_password']
        return id
    except:
        return None

def generate_secure_password() -> str:
    """Generate a secure random password"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"KES {amount:,.2f}"

def calculate_late_fees(due_amount: float, days_late: int, daily_rate: float = 0.001) -> float:
    """Calculate late payment fees"""
    if days_late <= 0:
        return 0.0
    
    late_fee = float(Decimal(str(due_amount)) * Decimal(str(daily_rate)) * Decimal(str(days_late)))
    return round(late_fee, 2)

def calculate_interest(principal: float, rate: float, days: int) -> float:
    """Calculate simple interest"""
    daily_rate = rate / 365
    interest = float(Decimal(str(principal)) * Decimal(str(daily_rate)) * Decimal(str(days)))
    return round(interest, 2)

def hash_password(password: str) -> str:
    """Generate password hash"""
    return generate_password_hash(password) 