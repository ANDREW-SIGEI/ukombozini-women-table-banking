from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User, Group, GroupMembership, Loan, LoanPayment,
    AgricultureCollection, SchoolFeesCollection, 
    GroupVisitReport, OfficerPerformance, ServiceFeeCollection
)
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
def get_monthly_report():
    """Generate a monthly report for all collections and activities."""
    current_user = get_jwt_identity()
    
    # Check authorization - only admin, manager or field officers
    if current_user['role'] not in ['admin', 'manager', 'field_officer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get month and year from query parameters or use current month
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', datetime.utcnow().month, type=int)
    officer_id = request.args.get('officer_id', current_user['id'] if current_user['role'] == 'field_officer' else None, type=int)
    
    # Get start and end date for the month
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    # Initialize report data
    report = {
        'period': {
            'month': month,
            'year': year,
            'start_date': start_date,
            'end_date': end_date
        },
        'officer': None,
        'collections': {
            'service_fees': 0.0,
            'registration_fees': 0.0,
            'new_member_fees': 0.0,
            'loan_collections': 0.0,
            'agriculture_collections': 0.0,
            'school_fees_collections': 0.0,
            'welfare_collections': 0.0,
            'total': 0.0
        },
        'loan_metrics': {
            'new_loans': 0,
            'total_disbursed': 0.0,
            'total_repaid': 0.0,
            'outstanding_balance': 0.0
        },
        'visit_metrics': {
            'groups_visited': 0,
            'total_attendance': 0,
            'avg_attendance': 0.0,
            'meetings_facilitated': 0,
            'issues_resolved': 0
        },
        'daily_reports': []
    }
    
    # If officer_id is specified, get officer details
    if officer_id:
        officer = User.query.get_or_404(officer_id)
        report['officer'] = {
            'id': officer.id,
            'name': f"{officer.first_name} {officer.last_name}",
            'role': officer.role,
            'email': officer.email,
            'phone_number': officer.phone_number
        }
    
    # Get performance metrics if available
    performance = OfficerPerformance.query.filter_by(
        officer_id=officer_id,
        month=month,
        year=year
    ).first() if officer_id else None
    
    if performance:
        report['visit_metrics']['groups_visited'] = performance.groups_visited
        report['visit_metrics']['meetings_facilitated'] = performance.meetings_attended
        report['visit_metrics']['issues_resolved'] = performance.issues_resolved
        report['visit_metrics']['avg_attendance'] = performance.avg_attendance
    
    # Build query filters
    date_filter = lambda col: (col >= start_date) & (col <= end_date)
    officer_filter = lambda col: col == officer_id if officer_id else True
    
    # Get service fee collections
    service_fee_query = ServiceFeeCollection.query.filter(
        date_filter(ServiceFeeCollection.collection_date)
    )
    
    if officer_id:
        service_fee_query = service_fee_query.filter_by(officer_id=officer_id)
    
    service_fees = service_fee_query.all()
    
    # Split service fees by type
    for fee in service_fees:
        if fee.fee_type == 'service':
            report['collections']['service_fees'] += float(fee.amount)
        elif fee.fee_type == 'registration':
            report['collections']['registration_fees'] += float(fee.amount)
        elif fee.fee_type == 'membership':
            report['collections']['new_member_fees'] += float(fee.amount)
        elif fee.fee_type == 'welfare':
            report['collections']['welfare_collections'] += float(fee.amount)
    
    # Get loan collections
    loan_payments = LoanPayment.query.filter(
        date_filter(LoanPayment.payment_date)
    ).all()
    
    report['collections']['loan_collections'] = sum(float(payment.amount) for payment in loan_payments)
    
    # Get agriculture collections
    agriculture_collections = AgricultureCollection.query.filter(
        date_filter(AgricultureCollection.collection_date),
        officer_filter(AgricultureCollection.user_id) if officer_id else True
    ).all()
    
    report['collections']['agriculture_collections'] = sum(float(collection.amount) for collection in agriculture_collections)
    
    # Get school fees collections
    school_fees_collections = SchoolFeesCollection.query.filter(
        date_filter(SchoolFeesCollection.payment_date),
        officer_filter(SchoolFeesCollection.user_id) if officer_id else True
    ).all()
    
    report['collections']['school_fees_collections'] = sum(float(collection.amount) for collection in school_fees_collections)
    
    # Get visit reports
    visit_reports = GroupVisitReport.query.filter(
        date_filter(GroupVisitReport.visit_date),
        officer_filter(GroupVisitReport.officer_id) if officer_id else True
    ).all()
    
    # Calculate daily reports
    daily_data = {}
    
    # Process service fees by day
    for fee in service_fees:
        day = fee.collection_date.day
        if day not in daily_data:
            daily_data[day] = {
                'date': datetime(year, month, day).strftime('%Y-%m-%d'),
                'loan_collections': 0.0,
                'agriculture_collections': 0.0,
                'school_fees_collections': 0.0,
                'service_fees': 0.0,
                'registration_fees': 0.0,
                'new_member_fees': 0.0,
                'welfare_collections': 0.0,
                'total': 0.0,
                'groups_visited': 0,
                'attendance': 0
            }
        
        # Add to correct fee type
        if fee.fee_type == 'service':
            daily_data[day]['service_fees'] += float(fee.amount)
        elif fee.fee_type == 'registration':
            daily_data[day]['registration_fees'] += float(fee.amount)
        elif fee.fee_type == 'membership':
            daily_data[day]['new_member_fees'] += float(fee.amount)
        elif fee.fee_type == 'welfare':
            daily_data[day]['welfare_collections'] += float(fee.amount)
        
        daily_data[day]['total'] += float(fee.amount)
    
    # Process loan payments by day
    for payment in loan_payments:
        day = payment.payment_date.day
        if day not in daily_data:
            daily_data[day] = {
                'date': datetime(year, month, day).strftime('%Y-%m-%d'),
                'loan_collections': 0.0,
                'agriculture_collections': 0.0,
                'school_fees_collections': 0.0,
                'service_fees': 0.0,
                'registration_fees': 0.0,
                'new_member_fees': 0.0,
                'welfare_collections': 0.0,
                'total': 0.0,
                'groups_visited': 0,
                'attendance': 0
            }
        daily_data[day]['loan_collections'] += float(payment.amount)
        daily_data[day]['total'] += float(payment.amount)
    
    # Process agriculture collections by day
    for collection in agriculture_collections:
        day = collection.collection_date.day
        if day not in daily_data:
            daily_data[day] = {
                'date': datetime(year, month, day).strftime('%Y-%m-%d'),
                'loan_collections': 0.0,
                'agriculture_collections': 0.0,
                'school_fees_collections': 0.0,
                'service_fees': 0.0,
                'registration_fees': 0.0,
                'new_member_fees': 0.0,
                'welfare_collections': 0.0,
                'total': 0.0,
                'groups_visited': 0,
                'attendance': 0
            }
        daily_data[day]['agriculture_collections'] += float(collection.amount)
        daily_data[day]['total'] += float(collection.amount)
    
    # Process school fees collections by day
    for collection in school_fees_collections:
        day = collection.payment_date.day
        if day not in daily_data:
            daily_data[day] = {
                'date': datetime(year, month, day).strftime('%Y-%m-%d'),
                'loan_collections': 0.0,
                'agriculture_collections': 0.0,
                'school_fees_collections': 0.0,
                'service_fees': 0.0,
                'registration_fees': 0.0,
                'new_member_fees': 0.0,
                'welfare_collections': 0.0,
                'total': 0.0,
                'groups_visited': 0,
                'attendance': 0
            }
        daily_data[day]['school_fees_collections'] += float(collection.amount)
        daily_data[day]['total'] += float(collection.amount)
    
    # Process visit reports by day
    for visit in visit_reports:
        day = visit.visit_date.day
        if day not in daily_data:
            daily_data[day] = {
                'date': datetime(year, month, day).strftime('%Y-%m-%d'),
                'loan_collections': 0.0,
                'agriculture_collections': 0.0,
                'school_fees_collections': 0.0,
                'service_fees': 0.0,
                'registration_fees': 0.0,
                'new_member_fees': 0.0,
                'welfare_collections': 0.0,
                'total': 0.0,
                'groups_visited': 0,
                'attendance': 0
            }
        daily_data[day]['groups_visited'] += 1
        daily_data[day]['attendance'] += visit.attendance_count or 0
    
    # Convert daily data to sorted list
    report['daily_reports'] = [daily_data[day] for day in sorted(daily_data.keys())]
    
    # Calculate overall totals
    report['collections']['total'] = (
        report['collections']['service_fees'] +
        report['collections']['registration_fees'] +
        report['collections']['new_member_fees'] +
        report['collections']['loan_collections'] +
        report['collections']['agriculture_collections'] +
        report['collections']['school_fees_collections'] +
        report['collections']['welfare_collections']
    )
    
    # Calculate visit metrics totals
    if visit_reports:
        report['visit_metrics']['total_attendance'] = sum(v.attendance_count or 0 for v in visit_reports)
        report['visit_metrics']['avg_attendance'] = (
            report['visit_metrics']['total_attendance'] / len(visit_reports)
            if len(visit_reports) > 0 else 0
        )
    
    return jsonify(report)

@reports_bp.route('/reports/field-officer-summary', methods=['GET'])
@jwt_required()
def get_field_officer_summary():
    """Get a summary of field officer performance for admin review."""
    current_user = get_jwt_identity()
    
    # Only admin or manager can access this report
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get month and year from query parameters or use current month
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', datetime.utcnow().month, type=int)
    
    # Get all field officers
    officers = User.query.filter_by(role='field_officer').all()
    
    # Get start and end date for the month
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    officer_summaries = []
    for officer in officers:
        # Get performance record
        performance = OfficerPerformance.query.filter_by(
            officer_id=officer.id,
            month=month,
            year=year
        ).first()
        
        # Get visit reports
        visit_reports = GroupVisitReport.query.filter(
            GroupVisitReport.officer_id == officer.id,
            GroupVisitReport.visit_date >= start_date,
            GroupVisitReport.visit_date <= end_date
        ).all()
        
        # Get collections
        service_fees = ServiceFeeCollection.query.filter(
            ServiceFeeCollection.officer_id == officer.id,
            ServiceFeeCollection.collection_date >= start_date,
            ServiceFeeCollection.collection_date <= end_date
        ).all()
        
        agriculture_collections = AgricultureCollection.query.filter(
            AgricultureCollection.user_id == officer.id,
            AgricultureCollection.collection_date >= start_date,
            AgricultureCollection.collection_date <= end_date
        ).all()
        
        school_fees_collections = SchoolFeesCollection.query.filter(
            SchoolFeesCollection.user_id == officer.id,
            SchoolFeesCollection.payment_date >= start_date,
            SchoolFeesCollection.payment_date <= end_date
        ).all()
        
        # Calculate collections by type
        service_fees_amount = sum(float(f.amount) for f in service_fees if f.fee_type == 'service')
        registration_fees_amount = sum(float(f.amount) for f in service_fees if f.fee_type == 'registration')
        membership_fees_amount = sum(float(f.amount) for f in service_fees if f.fee_type == 'membership')
        welfare_fees_amount = sum(float(f.amount) for f in service_fees if f.fee_type == 'welfare')
        
        # Create summary
        summary = {
            'officer_id': officer.id,
            'officer_name': f"{officer.first_name} {officer.last_name}",
            'month': month,
            'year': year,
            'groups_visited': len(set([v.group_id for v in visit_reports])),
            'total_visits': len(visit_reports),
            'total_attendance': sum(v.attendance_count or 0 for v in visit_reports),
            'performance_score': performance.performance_score if performance else None,
            'collections': {
                'service_fees': service_fees_amount,
                'registration_fees': registration_fees_amount,
                'membership_fees': membership_fees_amount,
                'welfare_fees': welfare_fees_amount,
                'agriculture': sum(float(c.amount) for c in agriculture_collections),
                'school_fees': sum(float(c.amount) for c in school_fees_collections),
                'total': (
                    service_fees_amount + 
                    registration_fees_amount + 
                    membership_fees_amount + 
                    welfare_fees_amount + 
                    sum(float(c.amount) for c in agriculture_collections) + 
                    sum(float(c.amount) for c in school_fees_collections)
                )
            },
            'status': 'Active' if officer.status == 'active' else 'Inactive'
        }
        
        officer_summaries.append(summary)
    
    return jsonify(officer_summaries) 