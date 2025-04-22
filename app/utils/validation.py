from app.utils.errors import ValidationError
import re
from datetime import datetime

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in the data"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f'Missing required fields: {", ".join(missing_fields)}')

def validate_email(email):
    """Validate email format"""
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_regex.match(email):
        raise ValidationError('Invalid email format')

def validate_phone_number(phone):
    """Validate phone number format"""
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(phone):
        raise ValidationError('Invalid phone number format')

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')

def validate_date(date_str, format='%Y-%m-%d'):
    """Validate date format"""
    try:
        datetime.strptime(date_str, format)
    except ValueError:
        raise ValidationError(f'Invalid date format. Expected format: {format}')

def validate_amount(amount):
    """Validate monetary amount"""
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0')
    except (TypeError, ValueError):
        raise ValidationError('Invalid amount format')

def validate_loan_request(data):
    """Validate loan request data"""
    required_fields = ['amount', 'interest_rate', 'term_months']
    validate_required_fields(data, required_fields)
    
    validate_amount(data['amount'])
    
    try:
        interest_rate = float(data['interest_rate'])
        if not 0 <= interest_rate <= 100:
            raise ValidationError('Interest rate must be between 0 and 100')
    except (TypeError, ValueError):
        raise ValidationError('Invalid interest rate format')
    
    try:
        term_months = int(data['term_months'])
        if term_months <= 0:
            raise ValidationError('Term months must be greater than 0')
    except (TypeError, ValueError):
        raise ValidationError('Invalid term months format')

def validate_payment(data):
    """Validate payment data"""
    required_fields = ['amount']
    validate_required_fields(data, required_fields)
    validate_amount(data['amount'])
    
    if 'payment_type' in data and data['payment_type'] not in ['cash', 'mobile_money', 'bank_transfer']:
        raise ValidationError('Invalid payment type')

def validate_collection(data):
    """Validate collection data"""
    required_fields = ['product_type', 'quantity', 'unit', 'unit_price']
    validate_required_fields(data, required_fields)
    
    validate_amount(data['quantity'])
    validate_amount(data['unit_price'])
    
    if len(data['product_type']) < 2:
        raise ValidationError('Product type must be at least 2 characters long')
    if len(data['unit']) < 1:
        raise ValidationError('Unit must be at least 1 character long') 