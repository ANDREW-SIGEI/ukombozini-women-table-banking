from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.field_officer import (
    FieldOfficerAssignment, Visit, OfficerRotation, 
    GroupVisitReport, OfficerPerformance, RotationHistory
)
from app.models.group import Group, GroupMembership
from app.models.financial import Loan, Saving
from app.models.collections import ServiceFeeCollection
from app.models.visit_report import VisitReport
from datetime import datetime, timedelta

field_officers_bp = Blueprint('field_officers', __name__)

# Field Officer Routes - For accessing groups they are assigned to
@field_officers_bp.route('/api/groups', methods=['GET'])
@login_required
def get_assigned_groups():
    """API endpoint to get groups assigned to the current field officer"""
    today = datetime.utcnow()
    
    # Get current assignments for this officer
    assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == current_user.id,
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today,
        FieldOfficerAssignment.status == 'active'
    ).all()
    
    groups = []
    for assignment in assignments:
        group = Group.query.get(assignment.group_id)
        if group:
            groups.append({
                'id': group.id,
                'name': group.name,
                'location': group.location,
                'description': group.description,
                'meeting_schedule': group.meeting_schedule,
                'status': group.status,
                'assignment_id': assignment.id,
                'rotation_start': assignment.rotation_start_date,
                'rotation_end': assignment.rotation_end_date
            })
    
    return jsonify(groups)

@field_officers_bp.route('/groups/<int:group_id>', methods=['GET'])
@login_required
def get_assigned_group(group_id):
    """Get details for a specific group assigned to the field officer"""
    today = datetime.utcnow()
    
    # Check if officer is assigned to this group
    assignment = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == current_user.id,
        FieldOfficerAssignment.group_id == group_id,
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today,
        FieldOfficerAssignment.status == 'active'
    ).first()
    
    if not assignment:
        return jsonify({'error': 'You are not currently assigned to this group'}), 403
    
    group = Group.query.get_or_404(group_id)
    
    return jsonify({
        'id': group.id,
        'name': group.name,
        'registration_number': group.registration_number,
        'location': group.location,
        'description': group.description,
        'meeting_schedule': group.meeting_schedule,
        'status': group.status,
        'assignment_id': assignment.id,
        'rotation_start': assignment.rotation_start_date,
        'rotation_end': assignment.rotation_end_date
    })

@field_officers_bp.route('/groups/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_assigned_group_members(group_id):
    current_user = get_jwt_identity()
    today = datetime.utcnow()
    
    # Check if officer is assigned to this group
    assignment = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == current_user['id'],
        FieldOfficerAssignment.group_id == group_id,
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today,
        FieldOfficerAssignment.status == 'active'
    ).first()
    
    if not assignment:
        return jsonify({'error': 'You are not currently assigned to this group'}), 403
    
    members = GroupMembership.query.filter_by(group_id=group_id, status='active')
    return jsonify([{
        'id': member.id,
        'role': member.role,
        'join_date': member.join_date,
        'user': {
            'id': member.user.id,
            'first_name': member.user.first_name,
            'last_name': member.user.last_name,
            'phone_number': member.user.phone_number,
            'email': member.user.email
        }
    } for member in members])

# Service Fees Collection Routes
@field_officers_bp.route('/service-fees', methods=['GET'])
@login_required
def get_service_fees():
    """Get service fees collected by the current field officer"""
    # Get filters
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    group_id = request.args.get('group_id', None)
    fee_type = request.args.get('fee_type', None)
    
    # Build query
    query = ServiceFeeCollection.query.filter_by(officer_id=current_user.id)
    
    if from_date:
        query = query.filter(ServiceFeeCollection.collection_date >= datetime.strptime(from_date, '%Y-%m-%d'))
    
    if to_date:
        query = query.filter(ServiceFeeCollection.collection_date <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if fee_type:
        query = query.filter_by(fee_type=fee_type)
    
    # Order by collection date, most recent first
    query = query.order_by(ServiceFeeCollection.collection_date.desc())
    
    fees = query.all()
    
    return jsonify([{
        'id': f.id,
        'group_id': f.group_id,
        'group_name': f.group.name if f.group else None,
        'fee_type': f.fee_type,
        'amount': float(f.amount),
        'collection_date': f.collection_date.isoformat() if f.collection_date else None,
        'payment_method': f.payment_method,
        'reference_number': f.reference_number,
        'notes': f.notes
    } for f in fees])

@field_officers_bp.route('/service-fees', methods=['POST'])
@login_required
def create_service_fee():
    """Create a new service fee collection"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['group_id', 'fee_type', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if officer is assigned to this group
    group_id = data.get('group_id')
    today = datetime.utcnow()
    
    assignment = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == current_user.id,
        FieldOfficerAssignment.group_id == group_id,
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today,
        FieldOfficerAssignment.status == 'active'
    ).first()
    
    if not assignment:
        return jsonify({'error': 'You are not currently assigned to this group'}), 403
    
    # Create service fee collection
    collection_date = datetime.strptime(data.get('collection_date'), '%Y-%m-%d') if data.get('collection_date') else today
    
    service_fee = ServiceFeeCollection(
        officer_id=current_user.id,
        group_id=group_id,
        visit_report_id=data.get('visit_report_id'),
        fee_type=data['fee_type'],
        amount=data['amount'],
        collection_date=collection_date,
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    
    db.session.add(service_fee)
    db.session.commit()
    
    return jsonify({
        'id': service_fee.id,
        'message': 'Service fee created successfully'
    }), 201

@field_officers_bp.route('/service-fees/<int:id>', methods=['PUT'])
@jwt_required()
def update_service_fee(id):
    current_user = get_jwt_identity()
    service_fee = ServiceFeeCollection.query.get_or_404(id)
    
    # Only allow officer who created it to update it
    if service_fee.officer_id != current_user['id']:
        return jsonify({'error': 'Unauthorized to update this fee collection'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'fee_type' in data:
        service_fee.fee_type = data['fee_type']
    
    if 'amount' in data:
        service_fee.amount = data['amount']
    
    if 'collection_date' in data:
        service_fee.collection_date = datetime.strptime(data['collection_date'], '%Y-%m-%d')
    
    if 'payment_method' in data:
        service_fee.payment_method = data['payment_method']
    
    if 'reference_number' in data:
        service_fee.reference_number = data['reference_number']
    
    if 'notes' in data:
        service_fee.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Service fee collection updated successfully',
        'id': service_fee.id
    })

@field_officers_bp.route('/service-fees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_service_fee(id):
    current_user = get_jwt_identity()
    service_fee = ServiceFeeCollection.query.get_or_404(id)
    
    # Only allow officer who created it or admin to delete it
    if service_fee.officer_id != current_user['id'] and current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized to delete this fee collection'}), 403
    
    db.session.delete(service_fee)
    db.session.commit()
    
    return jsonify({
        'message': 'Service fee collection deleted successfully'
    })

# Admin-specific service fee endpoints
@field_officers_bp.route('/admin/service-fees', methods=['GET'])
@jwt_required()
def admin_get_service_fees():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get filters
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    group_id = request.args.get('group_id', None)
    officer_id = request.args.get('officer_id', None)
    fee_type = request.args.get('fee_type', None)
    
    # Build query
    query = ServiceFeeCollection.query
    
    if from_date:
        query = query.filter(ServiceFeeCollection.collection_date >= datetime.strptime(from_date, '%Y-%m-%d'))
    
    if to_date:
        query = query.filter(ServiceFeeCollection.collection_date <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if officer_id:
        query = query.filter_by(officer_id=officer_id)
    
    if fee_type:
        query = query.filter_by(fee_type=fee_type)
    
    # Order by collection date, most recent first
    query = query.order_by(ServiceFeeCollection.collection_date.desc())
    
    fees = query.all()
    
    return jsonify([{
        'id': f.id,
        'officer_id': f.officer_id,
        'officer_name': f"{f.officer.first_name} {f.officer.last_name}" if f.officer else None,
        'group_id': f.group_id,
        'group_name': f.group.name if f.group else None,
        'fee_type': f.fee_type,
        'amount': float(f.amount),
        'collection_date': f.collection_date.isoformat() if f.collection_date else None,
        'payment_method': f.payment_method,
        'reference_number': f.reference_number,
        'notes': f.notes
    } for f in fees])

@field_officers_bp.route('/admin/service-fees/summary', methods=['GET'])
@jwt_required()
def admin_get_service_fees_summary():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get filters
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    group_id = request.args.get('group_id', None)
    
    # Set default date range to current month if not specified
    if not from_date and not to_date:
        today = datetime.utcnow()
        from_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
        # Last day of month
        next_month = today.replace(day=28) + timedelta(days=4)
        to_date = (next_month - timedelta(days=next_month.day)).strftime('%Y-%m-%d')
    
    # Parse dates
    start_date = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
    end_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1) if to_date else None
    
    # Build base query
    query = ServiceFeeCollection.query
    
    if start_date:
        query = query.filter(ServiceFeeCollection.collection_date >= start_date)
    
    if end_date:
        query = query.filter(ServiceFeeCollection.collection_date <= end_date)
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    # Get all fees
    all_fees = query.all()
    
    # Calculate summaries
    summary = {
        'period': {
            'from_date': from_date,
            'to_date': to_date
        },
        'total_collected': sum(float(f.amount) for f in all_fees),
        'fee_types': {},
        'by_officer': {},
        'by_group': {}
    }
    
    # Group by fee type
    for fee in all_fees:
        fee_type = fee.fee_type
        if fee_type not in summary['fee_types']:
            summary['fee_types'][fee_type] = 0
        summary['fee_types'][fee_type] += float(fee.amount)
        
        # Group by officer
        officer_id = fee.officer_id
        officer_name = f"{fee.officer.first_name} {fee.officer.last_name}" if fee.officer else f"Unknown ({officer_id})"
        
        if officer_id not in summary['by_officer']:
            summary['by_officer'][officer_id] = {
                'name': officer_name,
                'total': 0,
                'fee_types': {}
            }
        
        summary['by_officer'][officer_id]['total'] += float(fee.amount)
        
        if fee_type not in summary['by_officer'][officer_id]['fee_types']:
            summary['by_officer'][officer_id]['fee_types'][fee_type] = 0
        
        summary['by_officer'][officer_id]['fee_types'][fee_type] += float(fee.amount)
        
        # Group by group
        group_id = fee.group_id
        group_name = fee.group.name if fee.group else f"Unknown ({group_id})"
        
        if group_id not in summary['by_group']:
            summary['by_group'][group_id] = {
                'name': group_name,
                'total': 0,
                'fee_types': {}
            }
        
        summary['by_group'][group_id]['total'] += float(fee.amount)
        
        if fee_type not in summary['by_group'][group_id]['fee_types']:
            summary['by_group'][group_id]['fee_types'][fee_type] = 0
        
        summary['by_group'][group_id]['fee_types'][fee_type] += float(fee.amount)
    
    # Convert to lists for easier consumption in frontend
    summary['by_officer'] = [
        {
            'id': officer_id,
            'name': data['name'],
            'total': data['total'],
            'fee_types': [{'type': k, 'amount': v} for k, v in data['fee_types'].items()]
        }
        for officer_id, data in summary['by_officer'].items()
    ]
    
    summary['by_group'] = [
        {
            'id': group_id,
            'name': data['name'],
            'total': data['total'],
            'fee_types': [{'type': k, 'amount': v} for k, v in data['fee_types'].items()]
        }
        for group_id, data in summary['by_group'].items()
    ]
    
    summary['fee_types'] = [
        {'type': k, 'amount': v}
        for k, v in summary['fee_types'].items()
    ]
    
    return jsonify(summary)

# Visit Reports
@field_officers_bp.route('/visits', methods=['GET'])
@jwt_required()
def get_officer_visits():
    current_user = get_jwt_identity()
    
    # Get filters
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    group_id = request.args.get('group_id', None)
    status = request.args.get('status', None)
    
    # Build query
    query = GroupVisitReport.query.filter_by(officer_id=current_user['id'])
    
    if from_date:
        query = query.filter(GroupVisitReport.visit_date >= datetime.strptime(from_date, '%Y-%m-%d'))
    
    if to_date:
        query = query.filter(GroupVisitReport.visit_date <= datetime.strptime(to_date, '%Y-%m-%d'))
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by visit date, most recent first
    query = query.order_by(GroupVisitReport.visit_date.desc())
    
    visits = query.all()
    
    return jsonify([{
        'id': v.id,
        'assignment_id': v.assignment_id,
        'group_id': v.group_id,
        'group_name': v.group.name,
        'visit_date': v.visit_date,
        'attendance_count': v.attendance_count,
        'meeting_summary': v.meeting_summary,
        'issues_identified': v.issues_identified,
        'actions_taken': v.actions_taken,
        'recommendations': v.recommendations,
        'follow_up_required': v.follow_up_required,
        'follow_up_date': v.follow_up_date,
        'status': v.status
    } for v in visits])

@field_officers_bp.route('/visits', methods=['POST'])
@jwt_required()
def create_visit_report():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Check if officer is assigned to this group
    group_id = data.get('group_id')
    today = datetime.utcnow()
    
    assignment = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == current_user['id'],
        FieldOfficerAssignment.group_id == group_id,
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today,
        FieldOfficerAssignment.status == 'active'
    ).first()
    
    if not assignment:
        return jsonify({'error': 'You are not currently assigned to this group'}), 403
    
    # Create visit report
    visit_date = datetime.strptime(data.get('visit_date'), '%Y-%m-%d') if data.get('visit_date') else today
    
    report = GroupVisitReport(
        assignment_id=assignment.id,
        officer_id=current_user['id'],
        group_id=group_id,
        visit_date=visit_date,
        attendance_count=data.get('attendance_count'),
        meeting_summary=data.get('meeting_summary'),
        issues_identified=data.get('issues_identified'),
        actions_taken=data.get('actions_taken'),
        recommendations=data.get('recommendations'),
        follow_up_required=data.get('follow_up_required', False)
    )
    
    if data.get('follow_up_required') and data.get('follow_up_date'):
        report.follow_up_date = datetime.strptime(data.get('follow_up_date'), '%Y-%m-%d')
        report.follow_up_notes = data.get('follow_up_notes')
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'message': 'Visit report created successfully',
        'id': report.id
    }), 201

@field_officers_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_officer_performance():
    current_user = get_jwt_identity()
    
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', None, type=int)
    
    query = OfficerPerformance.query.filter_by(officer_id=current_user['id'], year=year)
    
    if month:
        query = query.filter_by(month=month)
    
    performance = query.order_by(OfficerPerformance.year.desc(), OfficerPerformance.month.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'month': p.month,
        'year': p.year,
        'groups_visited': p.groups_visited,
        'meetings_attended': p.meetings_attended,
        'issues_resolved': p.issues_resolved,
        'avg_attendance': p.avg_attendance,
        'performance_score': p.performance_score,
        'comments': p.comments
    } for p in performance])

@field_officers_bp.route('/api/rotation-history', methods=['GET'])
@login_required
def api_rotation_history():
    """API endpoint to get rotation history for the current field officer"""
    history = RotationHistory.query.filter_by(officer_id=current_user.id).order_by(RotationHistory.rotation_date.desc()).all()
    
    return jsonify([{
        'id': h.id,
        'prev_group_id': h.prev_group_id,
        'prev_group_name': h.prev_group.name if h.prev_group else None,
        'new_group_id': h.new_group_id,
        'new_group_name': h.new_group.name if h.new_group else None,
        'rotation_date': h.rotation_date,
        'reason': h.reason
    } for h in history])

# Admin Routes - For managing field officer assignments
@field_officers_bp.route('/admin/field-officers', methods=['GET'])
@jwt_required()
def get_field_officers():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    officers = User.query.filter_by(role='field_officer').all()
    return jsonify([{
        'id': o.id,
        'first_name': o.first_name,
        'last_name': o.last_name,
        'email': o.email,
        'phone_number': o.phone_number,
        'status': o.status
    } for o in officers])

@field_officers_bp.route('/admin/field-officers/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get filters
    officer_id = request.args.get('officer_id', None, type=int)
    group_id = request.args.get('group_id', None, type=int)
    status = request.args.get('status', None)
    
    # Build query
    query = FieldOfficerAssignment.query
    
    if officer_id:
        query = query.filter_by(officer_id=officer_id)
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if status:
        query = query.filter_by(status=status)
    
    assignments = query.order_by(FieldOfficerAssignment.rotation_end_date.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'officer_id': a.officer_id,
        'officer_name': f"{a.officer.first_name} {a.officer.last_name}",
        'group_id': a.group_id,
        'group_name': a.group.name,
        'rotation_start_date': a.rotation_start_date,
        'rotation_end_date': a.rotation_end_date,
        'status': a.status,
        'notes': a.notes
    } for a in assignments])

@field_officers_bp.route('/admin/field-officers/assignments', methods=['POST'])
@jwt_required()
def create_assignment():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['officer_id', 'group_id', 'rotation_start_date', 'rotation_end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Parse dates
    try:
        start_date = datetime.strptime(data['rotation_start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['rotation_end_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate date range
    if end_date <= start_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    # Check for overlapping assignments
    overlapping = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == data['officer_id'],
        FieldOfficerAssignment.status == 'active',
        FieldOfficerAssignment.rotation_start_date < end_date,
        FieldOfficerAssignment.rotation_end_date > start_date
    ).first()
    
    if overlapping:
        return jsonify({'error': 'Officer already has an overlapping assignment during this period'}), 400
    
    # Create assignment
    assignment = FieldOfficerAssignment(
        officer_id=data['officer_id'],
        group_id=data['group_id'],
        rotation_start_date=start_date,
        rotation_end_date=end_date,
        status='active',
        notes=data.get('notes')
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment created successfully',
        'id': assignment.id
    }), 201

@field_officers_bp.route('/admin/field-officers/assignments/<int:id>', methods=['PUT'])
@jwt_required()
def update_assignment(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = FieldOfficerAssignment.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields if provided
    if 'rotation_start_date' in data:
        try:
            assignment.rotation_start_date = datetime.strptime(data['rotation_start_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start date format. Use YYYY-MM-DD'}), 400
    
    if 'rotation_end_date' in data:
        try:
            assignment.rotation_end_date = datetime.strptime(data['rotation_end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid end date format. Use YYYY-MM-DD'}), 400
    
    # Validate date range
    if assignment.rotation_end_date <= assignment.rotation_start_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    if 'status' in data:
        assignment.status = data['status']
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment updated successfully',
        'id': assignment.id
    })

@field_officers_bp.route('/admin/field-officers/assignments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = FieldOfficerAssignment.query.get_or_404(id)
    
    # Soft delete by changing status
    assignment.status = 'inactive'
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment deactivated successfully'
    })

@field_officers_bp.route('/admin/field-officers/visits', methods=['GET'])
@jwt_required()
def admin_get_visits():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get filters
    officer_id = request.args.get('officer_id', None, type=int)
    group_id = request.args.get('group_id', None, type=int)
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    status = request.args.get('status', None)
    
    # Build query
    query = GroupVisitReport.query
    
    if officer_id:
        query = query.filter_by(officer_id=officer_id)
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if from_date:
        query = query.filter(GroupVisitReport.visit_date >= datetime.strptime(from_date, '%Y-%m-%d'))
    
    if to_date:
        query = query.filter(GroupVisitReport.visit_date <= datetime.strptime(to_date, '%Y-%m-%d'))
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by visit date, most recent first
    query = query.order_by(GroupVisitReport.visit_date.desc())
    
    visits = query.all()
    
    return jsonify([{
        'id': v.id,
        'officer_id': v.officer_id,
        'officer_name': f"{v.officer.first_name} {v.officer.last_name}",
        'group_id': v.group_id,
        'group_name': v.group.name,
        'visit_date': v.visit_date,
        'attendance_count': v.attendance_count,
        'meeting_summary': v.meeting_summary,
        'issues_identified': v.issues_identified,
        'actions_taken': v.actions_taken,
        'recommendations': v.recommendations,
        'follow_up_required': v.follow_up_required,
        'follow_up_date': v.follow_up_date,
        'status': v.status
    } for v in visits])

@field_officers_bp.route('/admin/field-officers/visits/<int:id>', methods=['PUT'])
@jwt_required()
def admin_update_visit(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    report = GroupVisitReport.query.get_or_404(id)
    data = request.get_json()
    
    # Admin can update status
    if 'status' in data:
        report.status = data['status']
    
    # Admin can add comments
    if 'admin_comments' in data:
        report.admin_comments = data['admin_comments']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Visit report updated successfully',
        'id': report.id
    })

@field_officers_bp.route('/admin/field-officers/<int:id>/performance', methods=['POST'])
@jwt_required()
def add_performance_metrics(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Check if officer exists
    officer = User.query.get_or_404(id)
    
    # Validate required fields
    required_fields = ['month', 'year', 'performance_score']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if performance record already exists for this month/year
    existing = OfficerPerformance.query.filter_by(
        officer_id=id,
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing:
        # Update existing record
        existing.groups_visited = data.get('groups_visited', existing.groups_visited)
        existing.meetings_attended = data.get('meetings_attended', existing.meetings_attended)
        existing.issues_resolved = data.get('issues_resolved', existing.issues_resolved)
        existing.avg_attendance = data.get('avg_attendance', existing.avg_attendance)
        existing.performance_score = data.get('performance_score', existing.performance_score)
        existing.comments = data.get('comments', existing.comments)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Performance metrics updated successfully',
            'id': existing.id
        })
    else:
        # Create new record
        performance = OfficerPerformance(
            officer_id=id,
            month=data['month'],
            year=data['year'],
            groups_visited=data.get('groups_visited', 0),
            meetings_attended=data.get('meetings_attended', 0),
            issues_resolved=data.get('issues_resolved', 0),
            avg_attendance=data.get('avg_attendance', 0.0),
            performance_score=data['performance_score'],
            comments=data.get('comments')
        )
        
        db.session.add(performance)
        db.session.commit()
        
        return jsonify({
            'message': 'Performance metrics added successfully',
            'id': performance.id
        }), 201

@field_officers_bp.route('/admin/field-officers/auto-rotate', methods=['POST'])
@jwt_required()
def auto_rotate_officers():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Get start and end dates for rotation
    try:
        start_date = datetime.strptime(data.get('start_date', ''), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date', ''), '%Y-%m-%d')
    except ValueError:
        # If dates not provided or invalid, use next month
        today = datetime.utcnow()
        start_date = datetime(today.year, today.month, 1) + timedelta(days=32)
        start_date = datetime(start_date.year, start_date.month, 1)  # First day of next month
        end_date = datetime(start_date.year, start_date.month + 1, 1) - timedelta(days=1)  # Last day of next month
    
    # Get active field officers
    officers = User.query.filter_by(role='field_officer', status='active').all()
    
    # Get active groups
    groups = Group.query.filter_by(status='active').all()
    
    # End any current assignments that overlap with new rotation period
    current_assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.status == 'active',
        FieldOfficerAssignment.rotation_end_date >= start_date
    ).all()
    
    for assignment in current_assignments:
        # If assignment ends after new rotation starts, end it at rotation start
        if assignment.rotation_end_date > start_date:
            assignment.rotation_end_date = start_date - timedelta(days=1)
            
            # Create rotation history
            history = RotationHistory(
                officer_id=assignment.officer_id,
                group_id=assignment.group_id,
                start_date=assignment.rotation_start_date,
                end_date=assignment.rotation_end_date,
                notes=f"Auto-ended for new rotation starting {start_date.strftime('%Y-%m-%d')}"
            )
            db.session.add(history)
    
    # Create new assignments
    new_assignments = []
    
    # Simple round-robin assignment algorithm
    # In a real application, this would be more sophisticated,
    # considering officer performance, group needs, etc.
    for i, group in enumerate(groups):
        officer = officers[i % len(officers)]
        
        assignment = FieldOfficerAssignment(
            officer_id=officer.id,
            group_id=group.id,
            rotation_start_date=start_date,
            rotation_end_date=end_date,
            status='active',
            notes=f"Auto-assigned for period {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        
        db.session.add(assignment)
        new_assignments.append({
            'officer_name': f"{officer.first_name} {officer.last_name}",
            'group_name': group.name,
            'start_date': start_date,
            'end_date': end_date
        })
    
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully rotated {len(new_assignments)} officers to new groups',
        'rotation_period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'assignments': new_assignments
    })

# Field Officer List
@field_officers_bp.route('/')
@login_required
def list_officers():
    # Get all users with field_officer role instead of FieldOfficer model
    officers = User.query.filter_by(role='field_officer').all()
    return render_template('field_officers/index.html', officers=officers)

@field_officers_bp.route('/view/<int:id>')
@login_required
def view_officer(id):
    # Get user with field_officer role
    officer = User.query.filter_by(id=id, role='field_officer').first_or_404()
    return render_template('field_officers/view.html', officer=officer)

# Field Officer Assignment Management
@field_officers_bp.route('/assignments')
@login_required
def assignment_management():
    # Modified to use User model instead of FieldOfficer
    officers = User.query.filter_by(role='field_officer').all()
    groups = Group.query.all()
    return render_template('field_officers/assignments.html', officers=officers, groups=groups)

@field_officers_bp.route('/rotation-history')
@login_required
def officer_rotation_history():
    """Display rotation history for all field officers"""
    # This could be replaced with actual rotation history model
    histories = RotationHistory.query.order_by(RotationHistory.rotation_date.desc()).limit(100).all()
    return render_template('field_officers/rotation_history.html', histories=histories)

# Visit Reports
@field_officers_bp.route('/visit-reports')
@login_required
def visit_reports():
    page = request.args.get('page', 1, type=int)
    officer_id = request.args.get('officer_id', type=int)
    group_id = request.args.get('group_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Base query
    query = VisitReport.query
    
    # Apply filters
    if officer_id:
        query = query.filter(VisitReport.officer_id == officer_id)
    if group_id:
        query = query.filter(VisitReport.group_id == group_id)
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(VisitReport.visit_date >= from_date_obj)
        except ValueError:
            pass
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(VisitReport.visit_date <= to_date_obj)
        except ValueError:
            pass
    
    # Paginate the results
    reports = query.order_by(VisitReport.visit_date.desc()).paginate(page=page, per_page=10)
    
    # Get all officers and groups for the filter dropdowns
    officers = User.query.all()
    groups = Group.query.all()
    
    return render_template(
        'field_officers/visit_reports.html',
        reports=reports.items,
        pagination=reports,
        officers=officers,
        groups=groups,
        officer_id=officer_id,
        group_id=group_id,
        from_date=from_date,
        to_date=to_date
    )

@field_officers_bp.route('/visit-reports/<int:id>')
@login_required
def view_report(id):
    report = VisitReport.query.get_or_404(id)
    officers = User.query.all()
    groups = Group.query.all()
    return render_template('field_officers/view_report.html', report=report, officers=officers, groups=groups)

@field_officers_bp.route('/visit-reports/create', methods=['POST'])
@login_required
def create_report():
    try:
        # Extract form data
        officer_id = request.form.get('officer_id', type=int)
        group_id = request.form.get('group_id', type=int)
        visit_date = request.form.get('visit_date')
        meeting_held = request.form.get('meeting_held') == 'true'
        attendance_percentage = request.form.get('attendance_percentage', type=int)
        status = request.form.get('status')
        report_content = request.form.get('report_content')
        challenges = request.form.get('challenges')
        recommendations = request.form.get('recommendations')
        
        # Validate required fields
        if not officer_id or not group_id or not visit_date or not report_content:
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('field_officers.visit_reports'))
        
        # Create new report
        visit_date_obj = datetime.strptime(visit_date, '%Y-%m-%d')
        report = VisitReport(
            officer_id=officer_id,
            group_id=group_id,
            visit_date=visit_date_obj,
            meeting_held=meeting_held,
            attendance_percentage=attendance_percentage if meeting_held else 0,
            status=status,
            report_content=report_content,
            challenges=challenges,
            recommendations=recommendations
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Visit report created successfully', 'success')
        return redirect(url_for('field_officers.view_report', id=report.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating report: {str(e)}', 'danger')
        return redirect(url_for('field_officers.visit_reports'))

@field_officers_bp.route('/visit-reports/<int:id>/update', methods=['POST'])
@login_required
def update_report(id):
    report = VisitReport.query.get_or_404(id)
    
    try:
        # Extract form data
        report.officer_id = request.form.get('officer_id', type=int)
        report.group_id = request.form.get('group_id', type=int)
        visit_date = request.form.get('visit_date')
        report.meeting_held = request.form.get('meeting_held') == 'true'
        report.attendance_percentage = request.form.get('attendance_percentage', type=int) if report.meeting_held else 0
        report.status = request.form.get('status')
        report.report_content = request.form.get('report_content')
        report.challenges = request.form.get('challenges')
        report.recommendations = request.form.get('recommendations')
        
        # Validate required fields
        if not report.officer_id or not report.group_id or not visit_date or not report.report_content:
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('field_officers.view_report', id=id))
        
        # Update visit date
        report.visit_date = datetime.strptime(visit_date, '%Y-%m-%d')
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Visit report updated successfully', 'success')
        return redirect(url_for('field_officers.view_report', id=id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating report: {str(e)}', 'danger')
        return redirect(url_for('field_officers.view_report', id=id))

@field_officers_bp.route('/visit-reports/<int:id>/delete', methods=['POST'])
@login_required
def delete_report(id):
    report = VisitReport.query.get_or_404(id)
    
    try:
        db.session.delete(report)
        db.session.commit()
        
        flash('Visit report deleted successfully', 'success')
        return redirect(url_for('field_officers.visit_reports'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
        return redirect(url_for('field_officers.view_report', id=id)) 