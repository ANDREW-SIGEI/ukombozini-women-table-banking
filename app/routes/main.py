from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from sqlalchemy import func
from datetime import datetime

# Import models directly from their modules
from app.models.user import User
from app.models.group import Group
from app.models.financial import Loan, Saving
from app.models.agriculture import AgricultureCollection
from app.models.school_fees import SchoolFeesCollection

bp = Blueprint('main', __name__)

# Home and Basic Pages
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'System is running normally'
    })

# Dashboard
@bp.route('/dashboard')
@login_required
def dashboard():
    # Get summary statistics
    total_users = User.query.count() if User else 0
    total_groups = Group.query.count() if Group else 0
    total_loans = Loan.query.count() if Loan else 0
    total_savings = Saving.query.count() if Saving else 0
    
    context = {
        'total_users': total_users,
        'total_groups': total_groups,
        'total_loans': total_loans,
        'total_savings': total_savings
    }
    
    return render_template('dashboard.html', **context)

@bp.route('/standalone-dashboard')
def standalone_dashboard():
    """Render the standalone dashboard template"""
    return render_template('standalone_dashboard.html')

@bp.route('/analytics-dashboard')
@login_required
def analytics_dashboard():
    return render_template('analytics_dashboard.html')

# User & Group Management
@bp.route('/members')
@login_required
def members():
    return render_template('members/index.html')

@bp.route('/field-officers')
@login_required
def field_officers():
    # Redirect to the field officers web blueprint
    return redirect(url_for('field_officers_web.list_officers'))

@bp.route('/field-officers/visit-reports')
@login_required
def field_officer_visit_reports():
    # Redirect to the field officer visit reports
    return redirect(url_for('field_officers_web.visit_reports'))

@bp.route('/field-officers/collection-summary')
@login_required
def field_officer_collection_summary():
    # Redirect to the field officer collection summary
    return redirect(url_for('field_officers_web.collection_summary'))

# Tablebanking Financial Management
@bp.route('/savings')
@login_required
def savings():
    return render_template('financial/savings.html')

@bp.route('/loans')
@login_required
def loans():
    return render_template('financial/loans.html')

@bp.route('/loan-collections')
@login_required
def loan_collections():
    return render_template('financial/loan_collections.html')

@bp.route('/dividends')
@login_required
def dividends():
    return render_template('financial/dividends.html')

@bp.route('/accounting')
@login_required
def accounting():
    return render_template('financial/accounting.html')

# Booster Collections
@bp.route('/agriculture-collection')
@login_required
def agriculture_collection():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    group_id = request.args.get('group_id', type=int)
    product_name = request.args.get('product_name')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Build the query
    query = AgricultureCollection.query
    
    # Apply filters if provided
    if group_id:
        query = query.filter(AgricultureCollection.group_id == group_id)
    if product_name:
        query = query.filter(AgricultureCollection.product_name.ilike(f'%{product_name}%'))
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(AgricultureCollection.collection_date >= from_date_obj)
        except ValueError:
            pass
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            to_date_obj = to_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(AgricultureCollection.collection_date <= to_date_obj)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(AgricultureCollection.collection_date.desc())
    
    # Paginate the results
    collections = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all groups and users for the dropdowns
    groups = Group.query.all()
    users = User.query.filter(User.is_active == True).all()
    
    return render_template('collections/agriculture.html', 
                          collections=collections.items,
                          pagination=collections,
                          groups=groups,
                          users=users)

@bp.route('/agriculture-monthly-collection')
@login_required
def agriculture_monthly_collection():
    return render_template('collections/agriculture_monthly.html')

@bp.route('/school-fees-collection')
@login_required
def school_fees_collection():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    group_id = request.args.get('group_id', type=int)
    student_name = request.args.get('student_name')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Build the query
    query = SchoolFeesCollection.query
    
    # Apply filters if provided
    if group_id:
        query = query.filter(SchoolFeesCollection.group_id == group_id)
    if student_name:
        query = query.filter(SchoolFeesCollection.student_name.ilike(f'%{student_name}%'))
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(SchoolFeesCollection.payment_date >= from_date_obj)
        except ValueError:
            pass
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            to_date_obj = to_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(SchoolFeesCollection.payment_date <= to_date_obj)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(SchoolFeesCollection.payment_date.desc())
    
    # Paginate the results
    collections = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all groups and users for the dropdowns
    groups = Group.query.all()
    users = User.query.filter(User.is_active == True).all()
    
    return render_template('collections/school_fees.html', 
                          collections=collections.items,
                          pagination=collections,
                          groups=groups,
                          users=users)

# Reports & Analytics
@bp.route('/tablebanking-reports')
@login_required
def tablebanking_reports():
    return render_template('reports/tablebanking.html')

@bp.route('/loan-reports')
@login_required
def loan_reports():
    return render_template('reports/loans.html')

# Ukombozini Management
@bp.route('/management-overview')
@login_required
def management_overview():
    return render_template('management/overview.html')

@bp.route('/settings')
@login_required
def settings():
    return render_template('management/settings.html')

# Ukombozini Financial Management
@bp.route('/products')
@login_required
def products():
    return render_template('products/index.html')

@bp.route('/group-loan')
@login_required
def group_loan():
    return render_template('loans/group_loan.html')

@bp.route('/individual-loan')
@login_required
def individual_loan():
    return render_template('loans/individual_loan.html')

# User Profile & Settings
@bp.route('/user-profile')
@login_required
def user_profile():
    return render_template('auth/profile.html')

@bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')

# Database Initialization
@bp.route('/init-db')
def init_db():
    """Initialize the database with tables and test users"""
    try:
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first() if User else None
        if not admin and User:
            # Create a test admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            admin.set_password('password')
            db.session.add(admin)
            
            # Create a test regular user
            user = User(
                username='user',
                email='user@example.com',
                first_name='Regular',
                last_name='User',
                role='member',
                is_active=True
            )
            user.set_password('password')
            db.session.add(user)
            
            db.session.commit()
            message = "Database initialized with admin and user accounts"
        else:
            message = "Admin user already exists"
            
        return jsonify({
            'status': 'success',
            'message': message,
            'users': [
                {'username': 'admin', 'password': 'password', 'role': 'admin'},
                {'username': 'user', 'password': 'password', 'role': 'member'}
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Test User Creation
@bp.route('/init-test-user')
def init_test_user():
    """Initialize a test user for development purposes"""
    if User and User.query.filter_by(username='admin').first():
        return jsonify({
            'status': 'success',
            'message': 'Test user already exists',
            'username': 'admin',
            'password': 'password'
        })
    
    if User:
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        user.set_password('password')
        
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Test user created successfully',
                'username': 'admin',
                'password': 'password'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    else:
        return jsonify({
            'status': 'error',
            'message': 'User model not found'
        }), 500 