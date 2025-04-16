from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from sqlalchemy import func

# Import models directly from their modules
from app.models.user import User
from app.models.group import Group
from app.models.financial import Loan, Saving

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
    return render_template('collections/agriculture.html')

@bp.route('/agriculture-monthly-collection')
@login_required
def agriculture_monthly_collection():
    return render_template('collections/agriculture_monthly.html')

@bp.route('/school-fees-collection')
@login_required
def school_fees_collection():
    return render_template('collections/school_fees.html')

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