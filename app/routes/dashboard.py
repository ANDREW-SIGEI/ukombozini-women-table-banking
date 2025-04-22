from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User, Group, Loan, Saving, Meeting, 
    GroupVisitReport, ServiceFeeCollection,
    FieldOfficerAssignment, OfficerPerformance,
    Visit, OfficerRotation, Collection, GroupMembership, LoanPayment
)
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar
import random

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Get an overview of key metrics for the dashboard."""
    current_user = get_jwt_identity()
    
    # Different metrics for different user roles
    if current_user['role'] == 'admin':
        # Admin sees global stats
        total_groups = Group.query.filter_by(status='active').count()
        total_members = User.query.filter_by(role='member', status='active').count()
        total_loans = Loan.query.count()
        total_savings = Saving.query.count()
        active_officers = User.query.filter_by(role='field_officer', status='active').count()
        today = datetime.utcnow().date()
        
        # Count today's scheduled meetings
        today_meetings = Meeting.query.filter(
            func.date(Meeting.date) == today
        ).count()
        
        # Count upcoming meetings in the next 7 days
        next_week = today + timedelta(days=7)
        upcoming_meetings = Meeting.query.filter(
            func.date(Meeting.date) > today,
            func.date(Meeting.date) <= next_week
        ).count()
        
        return jsonify({
            'total_groups': total_groups,
            'total_members': total_members,
            'active_officers': active_officers,
            'total_loans': total_loans,
            'total_savings': total_savings,
            'today_meetings': today_meetings,
            'upcoming_meetings': upcoming_meetings
        })
    
    elif current_user['role'] == 'field_officer':
        # Field officer sees only their assigned groups
        today = datetime.utcnow().date()
        
        # Get officer's currently assigned groups
        assignments = FieldOfficerAssignment.query.filter(
            FieldOfficerAssignment.officer_id == current_user['id'],
            FieldOfficerAssignment.rotation_start_date <= today,
            FieldOfficerAssignment.rotation_end_date >= today,
            FieldOfficerAssignment.status == 'active'
        ).all()
        
        assigned_group_ids = [a.group_id for a in assignments]
        
        # Get stats for assigned groups
        assigned_groups = len(assigned_group_ids)
        
        total_members = db.session.query(func.count(User.id)).join(
            User.group_memberships
        ).filter(
            User.role == 'member',
            User.status == 'active',
            User.group_memberships.any(group_id=assigned_group_ids)
        ).scalar() or 0
        
        # Count today's scheduled meetings
        today_meetings = Meeting.query.filter(
            func.date(Meeting.date) == today,
            Meeting.group_id.in_(assigned_group_ids)
        ).count()
        
        # Count upcoming meetings in the next 7 days
        next_week = today + timedelta(days=7)
        upcoming_meetings = Meeting.query.filter(
            func.date(Meeting.date) > today,
            func.date(Meeting.date) <= next_week,
            Meeting.group_id.in_(assigned_group_ids)
        ).count()
        
        # Get visit reports stats for this month
        current_month = today.month
        current_year = today.year
        first_day = datetime(current_year, current_month, 1)
        last_day = (datetime(current_year, current_month+1, 1) if current_month < 12 
                   else datetime(current_year+1, 1, 1)) - timedelta(days=1)
        
        visits_this_month = GroupVisitReport.query.filter(
            GroupVisitReport.officer_id == current_user['id'],
            GroupVisitReport.visit_date >= first_day,
            GroupVisitReport.visit_date <= last_day
        ).count()
        
        # Get performance metrics if available
        performance = OfficerPerformance.query.filter_by(
            officer_id=current_user['id'],
            month=current_month,
            year=current_year
        ).first()
        
        performance_score = performance.performance_score if performance else None
        
        # Get collections this month
        service_fees = db.session.query(func.sum(ServiceFeeCollection.amount)).filter(
            ServiceFeeCollection.officer_id == current_user['id'],
            ServiceFeeCollection.collection_date >= first_day,
            ServiceFeeCollection.collection_date <= last_day
        ).scalar() or 0
        
        return jsonify({
            'assigned_groups': assigned_groups,
            'total_members': total_members,
            'today_meetings': today_meetings,
            'upcoming_meetings': upcoming_meetings,
            'visits_this_month': visits_this_month,
            'performance_score': performance_score,
            'service_fees_collected': float(service_fees)
        })
    
    # Default for other users (members, etc.)
    return jsonify({
        'total_groups': Group.query.count(),
        'total_members': User.query.filter_by(role='member').count()
    })

@bp.route('/dashboard/field-officer', methods=['GET'])
@jwt_required()
def get_field_officer_dashboard():
    """Get dashboard data for field officers"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'field_officer':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get assigned groups
    assigned_groups = Group.query.filter_by(field_officer_id=current_user_id).all()
    group_ids = [group.id for group in assigned_groups]
    
    # Get today's date
    today = datetime.now().date()
    
    # Get today's meetings
    todays_meetings = Meeting.query.filter(
        Meeting.group_id.in_(group_ids),
        func.date(Meeting.date) == today,
        Meeting.status != 'cancelled'
    ).all()
    
    # Get recent visits (last 7 days)
    one_week_ago = today - timedelta(days=7)
    recent_visits = Visit.query.filter(
        Visit.field_officer_id == current_user_id,
        Visit.visit_date >= one_week_ago
    ).order_by(Visit.visit_date.desc()).limit(5).all()
    
    # Get collections
    collections = Collection.query.filter(
        Collection.group_id.in_(group_ids),
        func.date(Collection.collection_date) >= one_week_ago
    ).all()
    
    # Calculate total collections
    total_collections = sum(collection.amount for collection in collections)
    
    # Calculate performance score (simplified example)
    attendance_rate = 0.85  # Example value
    collection_efficiency = 0.9  # Example value
    visit_frequency = 0.8  # Example value
    performance_score = (attendance_rate + collection_efficiency + visit_frequency) / 3 * 10
    
    # Prepare response data
    response = {
        'assigned_groups': [
            {
                'id': group.id,
                'name': group.name,
                'location': group.location,
                'member_count': group.member_count,
                'meeting_day': group.meeting_day
            } for group in assigned_groups
        ],
        'todays_meetings': [
            {
                'id': meeting.id,
                'group_name': meeting.group.name,
                'location': meeting.group.location,
                'time': meeting.date.strftime('%H:%M'),
                'status': meeting.status
            } for meeting in todays_meetings
        ],
        'recent_visits': [
            {
                'id': visit.id,
                'group_name': visit.group.name,
                'visit_date': visit.visit_date.strftime('%Y-%m-%d'),
                'purpose': visit.purpose,
                'notes': visit.notes
            } for visit in recent_visits
        ],
        'collections': {
            'total': total_collections,
            'loan_repayments': sum(c.amount for c in collections if c.collection_type == 'loan_repayment'),
            'savings': sum(c.amount for c in collections if c.collection_type == 'savings'),
            'fees': sum(c.amount for c in collections if c.collection_type == 'fee')
        },
        'performance': {
            'score': round(performance_score, 1),
            'attendance_rate': attendance_rate * 100,
            'collection_efficiency': collection_efficiency * 100,
            'visit_frequency': visit_frequency * 100
        }
    }
    
    return jsonify(response)

@bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Get dashboard data for administrators"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get field officers
    field_officers = User.query.filter_by(role='field_officer').all()
    
    # Get total groups and unassigned groups
    total_groups = Group.query.count()
    unassigned_groups = Group.query.filter_by(field_officer_id=None).all()
    
    # Get meetings for this week
    today = datetime.now().date()
    end_of_week = today + timedelta(days=6 - today.weekday())
    meetings_this_week = Meeting.query.filter(
        func.date(Meeting.date) >= today,
        func.date(Meeting.date) <= end_of_week,
        Meeting.status != 'cancelled'
    ).count()
    
    # Get upcoming rotations
    upcoming_rotations = OfficerRotation.query.filter(
        OfficerRotation.rotation_date >= today,
        OfficerRotation.status == 'scheduled'
    ).order_by(OfficerRotation.rotation_date).all()
    
    # Get recent activity logs
    # This is a placeholder - in a real system, you would have an ActivityLog model
    recent_activities = [
        {
            'id': 1,
            'type': 'rotation',
            'description': 'Officer John Doe rotated from Group A to Group B',
            'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
            'user': 'Admin User'
        },
        {
            'id': 2,
            'type': 'assignment',
            'description': 'Group C assigned to Officer Jane Smith',
            'timestamp': (datetime.now() - timedelta(days=3)).isoformat(),
            'user': 'Admin User'
        },
        {
            'id': 3,
            'type': 'meeting',
            'description': 'Special meeting scheduled for all field officers',
            'timestamp': (datetime.now() - timedelta(days=5)).isoformat(),
            'user': 'Admin User'
        }
    ]
    
    # Prepare response data
    response = {
        'field_officers': [
            {
                'id': officer.id,
                'name': f"{officer.first_name} {officer.last_name}",
                'assigned_groups': Group.query.filter_by(field_officer_id=officer.id).all(),
                'performance_score': _calculate_performance_score(officer.id),
                'last_rotation': _get_last_rotation_date(officer.id),
                'upcoming_rotation': _get_upcoming_rotation(officer.id)
            } for officer in field_officers
        ],
        'total_groups': total_groups,
        'unassigned_groups': [
            {
                'id': group.id,
                'name': group.name,
                'location': group.location,
                'member_count': group.member_count,
                'created_at': group.created_at.isoformat() if group.created_at else None
            } for group in unassigned_groups
        ],
        'meetings_this_week': meetings_this_week,
        'upcoming_rotations': [
            {
                'id': rotation.id,
                'officer_id': rotation.field_officer_id,
                'officer_name': f"{rotation.field_officer.first_name} {rotation.field_officer.last_name}",
                'current_group': rotation.current_group.name,
                'new_group': rotation.new_group.name,
                'rotation_date': rotation.rotation_date.isoformat()
            } for rotation in upcoming_rotations
        ],
        'recent_activities': recent_activities
    }
    
    return jsonify(response)

def _calculate_performance_score(officer_id):
    """Calculate performance score for a field officer"""
    # In a real system, this would be based on actual metrics
    # For this example, we'll generate a random score between 6 and 9.5
    return round(random.uniform(6, 9.5), 1)

def _get_last_rotation_date(officer_id):
    """Get the date of the last rotation for an officer"""
    last_rotation = OfficerRotation.query.filter_by(
        field_officer_id=officer_id,
        status='completed'
    ).order_by(OfficerRotation.rotation_date.desc()).first()
    
    return last_rotation.rotation_date.isoformat() if last_rotation else None

def _get_upcoming_rotation(officer_id):
    """Get the upcoming rotation for an officer"""
    upcoming_rotation = OfficerRotation.query.filter_by(
        field_officer_id=officer_id,
        status='scheduled'
    ).order_by(OfficerRotation.rotation_date).first()
    
    if not upcoming_rotation:
        return None
    
    return {
        'id': upcoming_rotation.id,
        'date': upcoming_rotation.rotation_date.isoformat(),
        'current_group': upcoming_rotation.current_group.name,
        'new_group': upcoming_rotation.new_group.name
    }

@bp.route('/dashboard/member', methods=['GET'])
@jwt_required()
def get_member_dashboard():
    """Get dashboard data for members"""
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if not user or user.role != 'member':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get the dashboard data
    response = _get_member_dashboard_data(user)
    
    return jsonify(response)

@bp.route('/member/dashboard', methods=['GET'])
@jwt_required()
def member_dashboard_page():
    """Render the member dashboard page"""
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if not user or user.role != 'member':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard/member.html', title='Member Dashboard')

@bp.route('/api/dashboard/member', methods=['GET'])
@jwt_required()
def get_member_dashboard_api():
    """Get dashboard data for members (API endpoint)"""
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if not user or user.role != 'member':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get the dashboard data
    response = _get_member_dashboard_data(user)
    
    return jsonify(response)

def _get_member_dashboard_data(user):
    """Get dashboard data for a member"""
    today = datetime.utcnow().date()
    
    # Get the user's active loans
    active_loans = Loan.query.filter_by(
        user_id=user.id,
        status='active'
    ).all()
    
    # Get the user's savings transactions
    savings_transactions = Saving.query.filter_by(
        user_id=user.id
    ).order_by(Saving.created_at.desc()).all()
    
    # Calculate savings balance (sum of deposits minus withdrawals)
    savings_balance = 0
    for transaction in savings_transactions:
        if transaction.transaction_type == 'deposit':
            savings_balance += float(transaction.amount)
        elif transaction.transaction_type == 'withdrawal':
            savings_balance -= float(transaction.amount)
    
    # Get the user's group memberships
    group_memberships = GroupMembership.query.filter_by(
        user_id=user.id,
        status='active'
    ).all()
    group_ids = [membership.group_id for membership in group_memberships]
    
    # Get upcoming meetings for the user's groups
    upcoming_meetings = Meeting.query.filter(
        Meeting.group_id.in_(group_ids),
        Meeting.date >= today,
        Meeting.status != 'cancelled'
    ).order_by(Meeting.date).limit(5).all()
    
    # Create a list of the next 6 months for the savings chart
    months = []
    current_month = today.month
    current_year = today.year
    
    for i in range(6):
        month_num = (current_month - 5 + i) % 12
        if month_num == 0:
            month_num = 12
        year = current_year - 1 if current_month - 5 + i <= 0 else current_year
        month_name = calendar.month_name[month_num]
        months.append({'name': f"{month_name[:3]} {year}", 'month': month_num, 'year': year})
    
    # Get savings transactions for chart data
    savings_data = []
    for month_data in months:
        month = month_data['month']
        year = month_data['year']
        
        # Sum deposits for each month
        month_deposits = db.session.query(func.sum(Saving.amount)).filter(
            Saving.user_id == user.id,
            Saving.transaction_type == 'deposit',
            extract('month', Saving.created_at) == month,
            extract('year', Saving.created_at) == year
        ).scalar() or 0
        
        savings_data.append({
            'month': month_data['name'],
            'amount': float(month_deposits)
        })
    
    # Get next payment dates and amounts for active loans
    payment_schedule = []
    for loan in active_loans:
        # This is a simplified example - in a real system,
        # you would have a loan repayment schedule model
        # Here we're just creating an example payment
        next_payment_date = today + timedelta(days=random.randint(1, 30))
        
        # Calculate installment amount (simple calculation - would be more complex in real app)
        principal = float(loan.amount)
        rate = float(loan.interest_rate) / 100 / 12  # Monthly interest rate
        periods = loan.term_months
        installment_amount = principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)
        
        payment_schedule.append({
            'loan_id': loan.id,
            'loan_name': loan.loan_product.name if hasattr(loan, 'loan_product') else 'Loan',
            'due_date': next_payment_date.strftime('%Y-%m-%d'),
            'amount': round(installment_amount, 2),
            'status': 'upcoming'
        })
    
    # Sort payment schedule by due date
    payment_schedule.sort(key=lambda x: x['due_date'])
    
    # Get recent savings transactions for display
    recent_transactions = []
    for transaction in savings_transactions[:5]:
        recent_transactions.append({
            'date': transaction.created_at.strftime('%Y-%m-%d'),
            'type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'balance': savings_balance  # This is an approximation, would be more accurate in a real app
        })
        # Update balance for next transaction (showing how it would look historically)
        if transaction.transaction_type == 'deposit':
            savings_balance -= float(transaction.amount)
        elif transaction.transaction_type == 'withdrawal':
            savings_balance += float(transaction.amount)
    
    # Calculate outstanding balance for loans
    for loan in active_loans:
        # Simple calculation - in a real system would use actual payments
        # Simplified loan balance calculation
        loan.outstanding_balance = float(loan.amount)
        payments_sum = db.session.query(func.sum(LoanPayment.amount)).filter(
            LoanPayment.loan_id == loan.id
        ).scalar() or 0
        loan.outstanding_balance -= float(payments_sum)
    
    # Prepare the response
    response = {
        'user': {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'phone': user.phone_number,
            'email': user.email
        },
        'loans': {
            'count': len(active_loans),
            'data': [{
                'id': loan.id,
                'type': 'Personal Loan',  # Simplified since we don't have loan product
                'amount': float(loan.amount),
                'balance': loan.outstanding_balance,
                'due_date': loan.due_date.strftime('%Y-%m-%d') if loan.due_date else None,
                'status': loan.status
            } for loan in active_loans]
        },
        'savings': {
            'balance': savings_balance,
            'accounts': [{
                'id': 1,  # Simplified - in a real system would have separate accounts
                'type': 'Primary Savings',
                'balance': savings_balance
            }],
            'chart_data': savings_data,
            'recent_transactions': recent_transactions
        },
        'meetings': {
            'count': len(upcoming_meetings),
            'data': [{
                'id': meeting.id,
                'group': meeting.group.name,
                'date': meeting.date.strftime('%Y-%m-%d'),
                'time': meeting.date.strftime('%H:%M'),
                'location': meeting.location
            } for meeting in upcoming_meetings]
        },
        'payment_schedule': payment_schedule,
        'next_payment': payment_schedule[0] if payment_schedule else None
    }
    
    return response 