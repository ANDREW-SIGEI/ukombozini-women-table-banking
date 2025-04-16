from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.group import Group, GroupMembership
from app.models.field_officer import FieldOfficerAssignment, GroupVisitReport, OfficerPerformance, RotationHistory
from app.models.visit_report import VisitReport
from app.models.collections import ServiceFeeCollection, RegistrationFeeCollection, LoanCollection, ProjectFundCollection, WelfareCollection
from app.routes.financial import (
    get_service_fee, 
    get_project_registration_fee,
    get_member_registration_fee,
    get_ukombozini_loans_collected,
    get_ukombozini_project_funds,
    get_group_welfare_collected
)
from datetime import datetime, timedelta
from sqlalchemy import or_, func, and_

bp = Blueprint('field_officers_web', __name__)

@bp.route('/')
@login_required
def list_officers():
    """Display a list of all field officers"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    
    # Query with search if provided
    query = User.query.filter_by(role='field_officer')
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.phone_number.ilike(search_term)
            )
        )
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    officers = pagination.items
    
    # Prepare pagination links
    next_url = url_for('field_officers_web.list_officers', page=pagination.next_num, search=search) if pagination.has_next else None
    prev_url = url_for('field_officers_web.list_officers', page=pagination.prev_num, search=search) if pagination.has_prev else None
    
    return render_template(
        'field_officers/index.html',
        officers=officers,
        page=page,
        total_pages=pagination.pages,
        next_url=next_url,
        prev_url=prev_url,
        search=search
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_officer():
    """Create a new field officer"""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        
        # Validation
        if not username or not email or not password:
            flash('Username, email and password are required fields', 'danger')
            return render_template('field_officers/create.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('field_officers/create.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('field_officers/create.html')
        
        try:
            # Create new field officer
            officer = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='field_officer',
                is_active=True
            )
            officer.set_password(password)
            db.session.add(officer)
            db.session.commit()
            
            flash('Field officer created successfully', 'success')
            return redirect(url_for('field_officers_web.view_officer', id=officer.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating field officer: {str(e)}', 'danger')
            return render_template('field_officers/create.html')
    
    return render_template('field_officers/create.html')

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view_officer(id):
    """View a field officer's details"""
    officer = User.query.filter_by(id=id, role='field_officer').first_or_404()
    
    # Get current assignments
    today = datetime.utcnow()
    current_assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == id,
        FieldOfficerAssignment.status == 'active',
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today
    ).all()
    
    # Get past assignments
    past_assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == id,
        FieldOfficerAssignment.rotation_end_date < today
    ).order_by(FieldOfficerAssignment.rotation_end_date.desc()).limit(5).all()
    
    # Get all available groups for assignment
    available_groups = Group.query.filter_by(status='active').all()
    
    # Get latest performance metrics
    performance = OfficerPerformance.query.filter_by(officer_id=id).order_by(OfficerPerformance.evaluation_date.desc()).first()
    
    # Get recent visit reports
    visit_reports = VisitReport.query.filter_by(officer_id=id).order_by(VisitReport.visit_date.desc()).limit(5).all()
    
    return render_template(
        'field_officers/view.html',
        officer=officer,
        current_assignments=current_assignments,
        past_assignments=past_assignments,
        available_groups=available_groups,
        performance=performance,
        visit_reports=visit_reports
    )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_officer(id):
    """Edit a field officer's details"""
    officer = User.query.filter_by(id=id, role='field_officer').first_or_404()
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('new_password')
        
        # Validation
        if not username or not email:
            flash('Username and email are required fields', 'danger')
            return render_template('field_officers/edit.html', officer=officer)
        
        # Check if username already exists for different user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:
            flash('Username already exists', 'danger')
            return render_template('field_officers/edit.html', officer=officer)
        
        # Check if email already exists for different user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != id:
            flash('Email already exists', 'danger')
            return render_template('field_officers/edit.html', officer=officer)
        
        try:
            # Update officer
            officer.username = username
            officer.email = email
            officer.first_name = first_name
            officer.last_name = last_name
            officer.phone_number = phone_number
            officer.is_active = is_active
            
            # Update password if provided
            if new_password:
                officer.set_password(new_password)
            
            db.session.commit()
            flash('Field officer updated successfully', 'success')
            return redirect(url_for('field_officers_web.view_officer', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating field officer: {str(e)}', 'danger')
            return render_template('field_officers/edit.html', officer=officer)
    
    return render_template('field_officers/edit.html', officer=officer)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_officer(id):
    """Delete a field officer"""
    officer = User.query.filter_by(id=id, role='field_officer').first_or_404()
    
    try:
        # Set all active assignments to inactive
        active_assignments = FieldOfficerAssignment.query.filter_by(
            officer_id=id, 
            status='active'
        ).all()
        
        for assignment in active_assignments:
            assignment.status = 'inactive'
            assignment.rotation_end_date = datetime.utcnow()
        
        # Delete the field officer
        db.session.delete(officer)
        db.session.commit()
        
        flash('Field officer deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting field officer: {str(e)}', 'danger')
    
    return redirect(url_for('field_officers_web.list_officers'))

@bp.route('/assignments', methods=['GET'])
@login_required
def assignment_management():
    """Display assignment management page"""
    officers = User.query.filter_by(role='field_officer', is_active=True).all()
    groups = Group.query.filter_by(status='active').all()
    
    # Get current assignments
    today = datetime.utcnow()
    current_assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.status == 'active',
        FieldOfficerAssignment.rotation_start_date <= today,
        FieldOfficerAssignment.rotation_end_date >= today
    ).all()
    
    # Get upcoming assignments
    upcoming_assignments = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.status == 'active',
        FieldOfficerAssignment.rotation_start_date > today
    ).order_by(FieldOfficerAssignment.rotation_start_date).all()
    
    return render_template(
        'field_officers/assignments.html',
        officers=officers,
        groups=groups,
        current_assignments=current_assignments,
        upcoming_assignments=upcoming_assignments
    )

@bp.route('/assignments/create', methods=['POST'])
@login_required
def create_assignment():
    """Create a new field officer assignment"""
    officer_id = request.form.get('officer_id')
    group_id = request.form.get('group_id')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    notes = request.form.get('notes', '')
    
    if not officer_id or not group_id or not start_date_str or not end_date_str:
        flash('Officer, group, start date and end date are required fields', 'danger')
        return redirect(url_for('field_officers_web.assignment_management'))
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Check for existing active assignment for this group in the date range
        existing = FieldOfficerAssignment.query.filter(
            FieldOfficerAssignment.group_id == group_id,
            FieldOfficerAssignment.status == 'active',
            FieldOfficerAssignment.rotation_start_date <= end_date,
            FieldOfficerAssignment.rotation_end_date >= start_date
        ).first()
        
        if existing:
            flash('This group already has an active assignment in the specified date range', 'danger')
            return redirect(url_for('field_officers_web.assignment_management'))
        
        # Create the assignment
        assignment = FieldOfficerAssignment(
            officer_id=officer_id,
            group_id=group_id,
            rotation_start_date=start_date,
            rotation_end_date=end_date,
            status='active',
            notes=notes
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Record in rotation history
        history = RotationHistory(
            officer_id=officer_id,
            group_id=group_id,
            rotation_date=datetime.utcnow(),
            action_type='assigned',
            previous_officer_id=None,
            notes=f"Assigned from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        
        db.session.add(history)
        db.session.commit()
        
        flash('Field officer assignment created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating assignment: {str(e)}', 'danger')
    
    return redirect(url_for('field_officers_web.assignment_management'))

@bp.route('/assignments/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_assignment(id):
    """Cancel a field officer assignment"""
    assignment = FieldOfficerAssignment.query.get_or_404(id)
    
    try:
        assignment.status = 'cancelled'
        assignment.rotation_end_date = datetime.utcnow()
        
        db.session.commit()
        
        # Record in rotation history
        history = RotationHistory(
            officer_id=assignment.officer_id,
            group_id=assignment.group_id,
            rotation_date=datetime.utcnow(),
            action_type='cancelled',
            previous_officer_id=None,
            notes=f"Assignment cancelled"
        )
        
        db.session.add(history)
        db.session.commit()
        
        flash('Field officer assignment cancelled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling assignment: {str(e)}', 'danger')
    
    return redirect(url_for('field_officers_web.assignment_management'))

@bp.route('/rotation-history', methods=['GET'])
@login_required
def rotation_history():
    """Display rotation history"""
    histories = RotationHistory.query.order_by(RotationHistory.rotation_date.desc()).limit(100).all()
    return render_template('field_officers/rotation_history.html', histories=histories)

@bp.route('/visit-reports', methods=['GET'])
@login_required
def visit_reports():
    """Display field officer visit reports"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    officer_id = request.args.get('officer_id', None, type=int)
    group_id = request.args.get('group_id', None, type=int)
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    
    # Build query based on filters
    query = VisitReport.query
    
    if officer_id:
        query = query.filter_by(officer_id=officer_id)
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(VisitReport.visit_date >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(VisitReport.visit_date <= to_date_obj)
        except ValueError:
            pass
    
    # Get paginated results ordered by most recent first
    pagination = query.order_by(VisitReport.visit_date.desc()) \
                      .paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items
    
    # Get officers and groups for filter dropdowns
    officers = User.query.filter_by(role='field_officer').all()
    groups = Group.query.all()
    
    return render_template(
        'field_officers/visit_reports.html',
        reports=reports,
        officers=officers,
        groups=groups,
        pagination=pagination,
        officer_id=officer_id,
        group_id=group_id,
        from_date=from_date,
        to_date=to_date
    )

@bp.route('/performance-dashboard', methods=['GET'])
@login_required
def performance_dashboard():
    """Display field officer performance dashboard"""
    officers = User.query.filter_by(role='field_officer', is_active=True).all()
    
    # Get latest performance metrics for each officer
    performance_data = []
    for officer in officers:
        latest = OfficerPerformance.query.filter_by(officer_id=officer.id) \
                                   .order_by(OfficerPerformance.evaluation_date.desc()) \
                                   .first()
        if latest:
            performance_data.append({
                'officer': officer,
                'metrics': latest
            })
    
    return render_template(
        'field_officers/performance_dashboard.html',
        performance_data=performance_data
    )

@bp.route('/view-report/<int:id>', methods=['GET'])
@login_required
def view_report(id):
    """View a specific visit report"""
    report = VisitReport.query.get_or_404(id)
    officers = User.query.filter_by(role='field_officer').all()
    groups = Group.query.all()
    return render_template('field_officers/view_report.html', report=report, officers=officers, groups=groups)

@bp.route('/create-report', methods=['POST'])
@login_required
def create_report():
    """Create a new visit report"""
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
            return redirect(url_for('field_officers_web.visit_reports'))
        
        # Create new report
        visit_date_obj = datetime.strptime(visit_date, '%Y-%m-%d').date()
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
        return redirect(url_for('field_officers_web.view_report', id=report.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating report: {str(e)}', 'danger')
        return redirect(url_for('field_officers_web.visit_reports'))

@bp.route('/update-report/<int:id>', methods=['POST'])
@login_required
def update_report(id):
    """Update an existing visit report"""
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
            return redirect(url_for('field_officers_web.view_report', id=id))
        
        # Update visit date
        report.visit_date = datetime.strptime(visit_date, '%Y-%m-%d').date()
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Visit report updated successfully', 'success')
        return redirect(url_for('field_officers_web.view_report', id=id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating report: {str(e)}', 'danger')
        return redirect(url_for('field_officers_web.view_report', id=id))

@bp.route('/delete-report/<int:id>', methods=['POST'])
@login_required
def delete_report(id):
    """Delete a visit report"""
    report = VisitReport.query.get_or_404(id)
    
    try:
        db.session.delete(report)
        db.session.commit()
        
        flash('Visit report deleted successfully', 'success')
        return redirect(url_for('field_officers_web.visit_reports'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
        return redirect(url_for('field_officers_web.view_report', id=id))

@bp.route('/collection-summary')
@login_required
def collection_summary():
    """Generate daily collection summary report for field officers"""
    date_str = request.args.get('date')
    officer_id = request.args.get('officer_id', type=int)
    
    # Default to today if no date provided
    if not date_str:
        today = datetime.now().date()
        date_str = today.strftime('%Y-%m-%d')
    
    # Parse the date string
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
        return redirect(url_for('field_officers_web.collection_summary'))
    
    # Get all active field officers
    all_officers = User.query.filter_by(role='field_officer', is_active=True).all()
    
    # Generate daily summary report
    all_reports = generate_daily_summary_report(report_date, officer_id)
    
    # Calculate totals for summary section
    total_groups = sum(len(report['group_details']) for report in all_reports)
    total_amount = sum(report['totals']['total_amount_collected'] for report in all_reports)
    avg_per_group = total_amount / total_groups if total_groups > 0 else 0
    
    return render_template(
        'field_officers/collection_summary.html',
        date=date_str,
        officer_id=officer_id,
        all_officers=all_officers,
        reports=all_reports,
        total_groups=total_groups,
        total_amount=total_amount,
        avg_per_group=avg_per_group,
        today=datetime.now().date().strftime('%Y-%m-%d')
    )

@bp.route('/collection-summary/range')
@login_required
def collection_summary_range():
    """Generate collection summary report for field officers over a date range"""
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    officer_id = request.args.get('officer_id', type=int)
    
    # Default to last 7 days if no dates provided
    if not from_date_str or not to_date_str:
        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=7)
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')
    
    # Parse date strings
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
        return redirect(url_for('field_officers_web.collection_summary_range'))
    
    # Get all active field officers
    all_officers = User.query.filter_by(role='field_officer', is_active=True).all()
    
    # Generate reports for each day in the range
    date_range = [(from_date + timedelta(days=i)) for i in range((to_date - from_date).days + 1)]
    all_reports = []
    
    for date in date_range:
        daily_reports = generate_daily_summary_report(date, officer_id)
        if daily_reports:  # Only add days with reports
            all_reports.append({
                'date': date.strftime('%Y-%m-%d'),
                'reports': daily_reports
            })
    
    # Calculate range totals
    total_days = len(all_reports)
    total_groups_visited = sum(sum(len(report['group_details']) for report in day['reports']) for day in all_reports)
    total_amount_collected = sum(sum(report['totals']['total_amount_collected'] for report in day['reports']) for day in all_reports)
    
    # Calculate officer totals across all days
    officer_totals = {}
    for day in all_reports:
        for report in day['reports']:
            officer_id = report['officer_id']
            if officer_id not in officer_totals:
                officer_totals[officer_id] = {
                    'name': report['field_officer'],
                    'groups_visited': 0,
                    'total_collected': 0,
                    'service_fee': 0,
                    'project_reg_fee': 0,
                    'member_reg_fee': 0,
                    'ukombozini_loan': 0,
                    'ukombozini_project': 0,
                    'welfare': 0,
                    'days_active': 0
                }
            
            officer_totals[officer_id]['groups_visited'] += len(report['group_details'])
            officer_totals[officer_id]['total_collected'] += report['totals']['total_amount_collected']
            officer_totals[officer_id]['service_fee'] += report['totals']['service_fee']
            officer_totals[officer_id]['project_reg_fee'] += report['totals']['project_registration_fee']
            officer_totals[officer_id]['member_reg_fee'] += report['totals']['member_registration_fee']
            officer_totals[officer_id]['ukombozini_loan'] += report['totals']['ukombozini_loan_collection']
            officer_totals[officer_id]['ukombozini_project'] += report['totals']['ukombozini_project_amount']
            officer_totals[officer_id]['welfare'] += report['totals']['welfare_total']
            officer_totals[officer_id]['days_active'] += 1
    
    return render_template(
        'field_officers/collection_summary_range.html',
        from_date=from_date_str,
        to_date=to_date_str,
        officer_id=officer_id,
        all_officers=all_officers,
        all_reports=all_reports,
        total_days=total_days,
        total_groups_visited=total_groups_visited,
        total_amount_collected=total_amount_collected,
        officer_totals=officer_totals,
        today=datetime.now().date().strftime('%Y-%m-%d')
    )

def get_field_officer_data(date, officer_id=None):
    """Get list of all field officers active on this day"""
    query = User.query.filter_by(role='field_officer', is_active=True)
    
    if officer_id:
        query = query.filter_by(id=officer_id)
    
    officers = query.all()
    
    result = [{
        'id': officer.id,
        'name': f"{officer.first_name} {officer.last_name}",
        'username': officer.username,
        'email': officer.email,
        'phone_number': officer.phone_number
    } for officer in officers]
    
    # If no officers found, add a demo officer for testing
    if not result:
        # Try to find any user that could be used as a demo officer
        demo_user = User.query.first()
        if demo_user:
            result.append({
                'id': demo_user.id,
                'name': f"{demo_user.first_name} {demo_user.last_name} (Demo)",
                'username': demo_user.username,
                'email': demo_user.email,
                'phone_number': demo_user.phone_number
            })
        else:
            # Create a hardcoded demo officer if no users exist
            result.append({
                'id': 999,
                'name': "Demo Field Officer",
                'username': "demo_officer",
                'email': "demo@example.com",
                'phone_number': "1234567890"
            })
    
    return result

def get_attended_groups(officer_id, date):
    """Get groups attended by a field officer on a specific date"""
    # Convert string date to datetime object if needed
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Find groups assigned to this officer
    assigned_groups = FieldOfficerAssignment.query.filter(
        FieldOfficerAssignment.officer_id == officer_id,
        FieldOfficerAssignment.status == 'active',
        func.date(FieldOfficerAssignment.rotation_start_date) <= date,
        (FieldOfficerAssignment.rotation_end_date == None) | (func.date(FieldOfficerAssignment.rotation_end_date) >= date)
    ).all()
    
    # Get group details for each assigned group
    groups = []
    for assignment in assigned_groups:
        group = Group.query.get(assignment.group_id)
        if group:
            # Check if there was a visit report for this date
            visit_report = VisitReport.query.filter(
                VisitReport.officer_id == officer_id,
                VisitReport.group_id == group.id,
                func.date(VisitReport.visit_date) == date
            ).first()
            
            # Get member count
            member_count = GroupMembership.query.filter_by(
                group_id=group.id,
                status='active'
            ).count()
            
            # Get attendees count from visit report if available, or use a default
            attendees_count = 0
            if visit_report and visit_report.attendance_percentage > 0:
                attendees_count = int(member_count * (visit_report.attendance_percentage / 100))
            else:
                # Use a default attendance of 70% for demo purposes
                attendees_count = int(member_count * 0.7)
            
            groups.append({
                'id': group.id,
                'name': group.name,
                'location': group.location,
                'member_count': member_count,
                'attendees_count': attendees_count,
                'visit_report_id': visit_report.id if visit_report else None
            })
    
    # If no assigned groups are found, add at least one test group for demo purposes
    if not groups and officer_id:
        # Find any group to use as demo
        demo_group = Group.query.first()
        if demo_group:
            groups.append({
                'id': demo_group.id,
                'name': f"{demo_group.name} (Demo)",
                'location': demo_group.location,
                'member_count': 20,
                'attendees_count': 15,
                'visit_report_id': None
            })
    
    return groups

def generate_daily_summary_report(date, officer_id=None):
    """Generate daily collection summary report for field officers"""
    all_reports = []

    # Step 1: Get list of all field officers active on this day
    field_officers = get_field_officer_data(date, officer_id)

    for officer in field_officers:
        officer_name = officer['name']
        officer_id = officer['id']

        # Step 2: Get groups attended by this officer
        groups = get_attended_groups(officer_id, date)

        total_service_fee = 0
        total_project_reg_fee = 0
        total_member_reg_fee = 0
        total_ukombozini_loan = 0
        total_ukombozini_projects = 0
        total_welfare = 0

        group_details = []

        for group in groups:
            group_name = group['name']
            group_id = group['id']
            group_attendees = group['attendees_count']

            # Step 3: Retrieve financials per group
            service_fee = get_service_fee(group_id, date)
            project_fee = get_project_registration_fee(group_id, date)
            member_fee = get_member_registration_fee(group_id, date)
            ukombozini_loan = get_ukombozini_loans_collected(group_id, date)
            ukombozini_project = get_ukombozini_project_funds(group_id, date)
            welfare_fee = get_group_welfare_collected(group_id, date)

            total_service_fee += service_fee
            total_project_reg_fee += project_fee
            total_member_reg_fee += member_fee
            total_ukombozini_loan += ukombozini_loan
            total_ukombozini_projects += ukombozini_project
            total_welfare += welfare_fee

            group_total = service_fee + project_fee + member_fee + ukombozini_loan + ukombozini_project + welfare_fee
            
            if group_total > 0:  # Only include groups with collections
                group_details.append({
                    "group_name": group_name,
                    "attendees": group_attendees,
                    "service_fee": service_fee,
                    "project_reg_fee": project_fee,
                    "member_reg_fee": member_fee,
                    "ukombozini_loan_collected": ukombozini_loan,
                    "ukombozini_project_fund": ukombozini_project,
                    "welfare_collected": welfare_fee,
                    "group_total": group_total
                })

        # Step 4: Calculate officer total collection
        officer_total = (
            total_service_fee +
            total_project_reg_fee +
            total_member_reg_fee +
            total_ukombozini_loan +
            total_ukombozini_projects +
            total_welfare
        )
        
        # Only include officers with collections
        if officer_total > 0 and group_details:
            # Find most and least paying groups
            most_paying_group = None
            least_paying_group = None
            
            if group_details:
                most_paying = max(group_details, key=lambda x: x["group_total"])
                least_paying = min(group_details, key=lambda x: x["group_total"])
                most_paying_group = most_paying["group_name"]
                least_paying_group = least_paying["group_name"]
            
            # Step 5: Build officer report
            officer_report = {
                "date": date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else date,
                "officer_id": officer_id,
                "field_officer": officer_name,
                "groups_attended": len(groups),
                "group_details": group_details,
                "totals": {
                    "service_fee": total_service_fee,
                    "project_registration_fee": total_project_reg_fee,
                    "member_registration_fee": total_member_reg_fee,
                    "ukombozini_loan_collection": total_ukombozini_loan,
                    "ukombozini_project_amount": total_ukombozini_projects,
                    "welfare_total": total_welfare,
                    "total_amount_collected": officer_total
                },
                "analytics": {
                    "average_collection_per_group": officer_total / len(group_details) if group_details else 0,
                    "most_paying_group": most_paying_group,
                    "least_paying_group": least_paying_group
                }
            }

            all_reports.append(officer_report)

    return all_reports

def export_to_excel(report_data, date):
    """Export collection summary to Excel"""
    from io import BytesIO
    import pandas as pd
    
    # Create Excel workbook
    output = BytesIO()
    
    # Convert to list format if it's a single officer report
    if not isinstance(report_data, list):
        report_data = [report_data]
    
    # Create summary sheet
    summary_data = {
        'Officer': [],
        'Groups Attended': [],
        'Service Fee': [],
        'Project Registration': [],
        'Member Registration': [],
        'Ukombozini Loan': [],
        'Ukombozini Project': [],
        'Welfare': [],
        'Total Collected': []
    }
    
    for report in report_data:
        summary_data['Officer'].append(report['Field Officer'])
        summary_data['Groups Attended'].append(report['Groups Attended'])
        summary_data['Service Fee'].append(report['Totals']['Service Fee'])
        summary_data['Project Registration'].append(report['Totals']['Project Registration Fee'])
        summary_data['Member Registration'].append(report['Totals']['Member Registration Fee'])
        summary_data['Ukombozini Loan'].append(report['Totals']['Ukombozini Loan Collection'])
        summary_data['Ukombozini Project'].append(report['Totals']['Ukombozini Project Amount'])
        summary_data['Welfare'].append(report['Totals']['Welfare Total'])
        summary_data['Total Collected'].append(report['Totals']['Total Amount Collected'])
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Add total row
    summary_df.loc['Total'] = summary_df.sum(numeric_only=True)
    summary_df.at['Total', 'Officer'] = 'TOTAL'
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write summary sheet
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and summary worksheet
        workbook = writer.book
        summary_sheet = writer.sheets['Summary']
        
        # Add formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D8E4BC', 'border': 1})
        total_format = workbook.add_format({'bold': True, 'bg_color': '#E6E6E6', 'border': 1})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        
        # Apply formats to summary sheet
        for col_num, value in enumerate(summary_df.columns.values):
            summary_sheet.write(0, col_num, value, header_format)
        
        # Format totals row
        for col_num in range(len(summary_df.columns)):
            summary_sheet.write(len(summary_df), col_num, summary_df.iloc[-1, col_num], total_format)
        
        # Apply money format to amount columns
        for col_num in range(2, len(summary_df.columns)):
            summary_sheet.set_column(col_num, col_num, 15, money_format)
        
        # Add detailed sheets for each officer
        for report in report_data:
            officer_name = report['Field Officer'].replace(' ', '_')[:31]  # Sheet name length limit
            
            # Create group details DataFrame
            if report['Group Details']:
                group_df = pd.DataFrame(report['Group Details'])
                group_df.to_excel(writer, sheet_name=officer_name, index=False)
                
                # Format group details sheet
                details_sheet = writer.sheets[officer_name]
                for col_num, value in enumerate(group_df.columns.values):
                    details_sheet.write(0, col_num, value, header_format)
    
    # Set file headers for download
    output.seek(0)
    report_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
    filename = f"Collection_Summary_{report_date}.xlsx"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def export_range_to_excel(daily_reports, summary_data, from_date, to_date):
    """Export date range collection summary to Excel"""
    from io import BytesIO
    import pandas as pd
    
    # Create Excel workbook
    output = BytesIO()
    
    # Create summary DataFrame
    summary_df = pd.DataFrame({
        'Date Range': [summary_data['Date Range']],
        'Days in Range': [summary_data['Days in Range']],
        'Days with Collections': [summary_data['Days with Collections']],
        'Collection Rate (%)': [f"{summary_data['Collection Rate']:.2f}%"],
        'Total Groups Attended': [summary_data['Total Groups Attended']],
        'Total Collection': [summary_data['Totals']['Total Amount Collected']]
    })
    
    # Create totals by category DataFrame
    totals_df = pd.DataFrame({
        'Category': ['Service Fee', 'Project Registration', 'Member Registration', 
                    'Ukombozini Loan', 'Ukombozini Project', 'Welfare', 'Total'],
        'Amount': [
            summary_data['Totals']['Service Fee'],
            summary_data['Totals']['Project Registration Fee'],
            summary_data['Totals']['Member Registration Fee'],
            summary_data['Totals']['Ukombozini Loan Collection'],
            summary_data['Totals']['Ukombozini Project Amount'],
            summary_data['Totals']['Welfare Total'],
            summary_data['Totals']['Total Amount Collected']
        ]
    })
    
    # Create officer performance DataFrame
    officers_df = pd.DataFrame([
        {
            'Officer': officer['name'],
            'Total Collected': officer['total_collected'],
            'Groups Attended': officer['groups_attended'],
            'Days Active': officer['days_active'],
            'Avg per Day': officer['average_per_day'],
            'Avg per Group': officer['average_per_group']
        }
        for officer in summary_data['Officer Performance']
    ])
    
    # Create daily reports DataFrame
    daily_data = []
    for report in daily_reports:
        daily_data.append({
            'Date': report['Date'],
            'Officer': report['Field Officer'],
            'Groups Attended': report['Groups Attended'],
            'Total Collected': report['Totals']['Total Amount Collected']
        })
    
    daily_df = pd.DataFrame(daily_data)
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write summary sheet
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        totals_df.to_excel(writer, sheet_name='Summary', startrow=len(summary_df) + 2, index=False)
        officers_df.to_excel(writer, sheet_name='Officer Performance', index=False)
        daily_df.to_excel(writer, sheet_name='Daily Reports', index=False)
        
        # Get workbook and summary worksheet
        workbook = writer.book
        summary_sheet = writer.sheets['Summary']
        performance_sheet = writer.sheets['Officer Performance']
        daily_sheet = writer.sheets['Daily Reports']
        
        # Add formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D8E4BC', 'border': 1})
        total_format = workbook.add_format({'bold': True, 'bg_color': '#E6E6E6', 'border': 1})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        
        # Apply formats
        for sheet in [summary_sheet, performance_sheet, daily_sheet]:
            # Format headers
            for col_num in range(10):  # Assume max 10 columns
                sheet.set_column(col_num, col_num, 15)
    
    # Set file headers for download
    output.seek(0)
    from_date_str = datetime.strptime(from_date, '%Y-%m-%d').strftime('%Y%m%d')
    to_date_str = datetime.strptime(to_date, '%Y-%m-%d').strftime('%Y%m%d')
    filename = f"Collection_Summary_{from_date_str}_to_{to_date_str}.xlsx"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def export_to_pdf(report_data, date):
    """Export collection summary to PDF"""
    # This function would generate a PDF document
    # Using a library like WeasyPrint or ReportLab
    
    # For now, we'll return a simplified implementation
    from flask import make_response
    
    # Convert the template to HTML first
    if not isinstance(report_data, list):
        report_data = [report_data]
    
    html = render_template(
        'field_officers/pdf_templates/collection_summary_pdf.html',
        report_data=report_data,
        date=date
    )
    
    # Create a simple PDF response
    response = make_response(html)
    report_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
    filename = f"Collection_Summary_{report_date}.pdf"
    
    # In a real implementation, we would convert HTML to PDF here
    # For now, we'll return HTML with PDF headers
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_range_to_pdf(daily_reports, summary_data, from_date, to_date):
    """Export date range collection summary to PDF"""
    # This function would generate a PDF document
    # Using a library like WeasyPrint or ReportLab
    
    # For now, we'll return a simplified implementation
    from flask import make_response
    
    html = render_template(
        'field_officers/pdf_templates/collection_summary_range_pdf.html',
        daily_reports=daily_reports,
        summary_data=summary_data,
        from_date=from_date,
        to_date=to_date
    )
    
    # Create a simple PDF response
    response = make_response(html)
    from_date_str = datetime.strptime(from_date, '%Y-%m-%d').strftime('%Y%m%d')
    to_date_str = datetime.strptime(to_date, '%Y-%m-%d').strftime('%Y%m%d')
    filename = f"Collection_Summary_{from_date_str}_to_{to_date_str}.pdf"
    
    # In a real implementation, we would convert HTML to PDF here
    # For now, we'll return HTML with PDF headers
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

# New routes for collection entry
@bp.route('/collection-entry')
@login_required
def collection_entry():
    """Display form for entering collection data"""
    # Get current date
    today = datetime.now().date().strftime('%Y-%m-%d')
    
    # Get list of field officers
    all_officers = User.query.filter_by(role='field_officer', is_active=True).all()
    
    # Get assigned groups - if current user is a field officer, show only their groups
    assigned_groups = []
    if current_user.role == 'field_officer':
        # Get groups assigned to this field officer
        assignments = FieldOfficerAssignment.query.filter_by(
            officer_id=current_user.id,
            status='active'
        ).all()
        
        for assignment in assignments:
            group = Group.query.get(assignment.group_id)
            if group:
                assigned_groups.append(group)
    elif current_user.role == 'admin':
        # For admin, we'll load groups dynamically based on selected officer
        assigned_groups = []
    
    return render_template(
        'field_officers/collection_entry.html',
        today=today,
        all_officers=all_officers,
        assigned_groups=assigned_groups
    )

@bp.route('/api/officer/<int:officer_id>/groups')
@login_required
def get_officer_groups(officer_id):
    """API endpoint to get groups assigned to a field officer"""
    # Check permissions
    if current_user.role != 'admin' and current_user.id != officer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get active assignments for this officer
    assignments = FieldOfficerAssignment.query.filter_by(
        officer_id=officer_id,
        status='active'
    ).all()
    
    groups = []
    for assignment in assignments:
        group = Group.query.get(assignment.group_id)
        if group:
            groups.append({
                'id': group.id,
                'name': group.name,
                'location': group.location
            })
    
    return jsonify(groups)

@bp.route('/save-collection', methods=['POST'])
@login_required
def save_collection():
    """Save collection data from form submission"""
    # Check if request is AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Get form data
        collection_date = datetime.strptime(request.form.get('collection_date'), '%Y-%m-%d').date()
        officer_id = int(request.form.get('officer_id'))
        group_id = int(request.form.get('group_id'))
        
        # Check if user is authorized to submit for this officer
        if current_user.role != 'admin' and current_user.id != officer_id:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Unauthorized: You can only submit collections for yourself.'}), 403
            flash('Unauthorized: You can only submit collections for yourself.', 'danger')
            return redirect(url_for('field_officers_web.collection_entry'))
        
        # Check if officer is assigned to this group
        assignment = FieldOfficerAssignment.query.filter_by(
            officer_id=officer_id,
            group_id=group_id,
            status='active'
        ).first()
        
        if not assignment:
            if is_ajax:
                return jsonify({'success': False, 'message': 'This officer is not assigned to the selected group.'}), 400
            flash('This officer is not assigned to the selected group.', 'danger')
            return redirect(url_for('field_officers_web.collection_entry'))
        
        # Get attendance data
        meeting_held = request.form.get('meeting_held') == 'yes'
        attendance_percentage = int(request.form.get('attendance_percentage', 0)) if meeting_held else 0
        meeting_notes = request.form.get('meeting_notes', '')
        
        # Create or update visit report
        visit_report = VisitReport.query.filter_by(
            officer_id=officer_id,
            group_id=group_id,
            visit_date=collection_date
        ).first()
        
        if not visit_report:
            visit_report = VisitReport(
                officer_id=officer_id,
                group_id=group_id,
                visit_date=collection_date,
                meeting_held=meeting_held,
                attendance_percentage=attendance_percentage,
                status='submitted',
                report_content=meeting_notes,
                challenges='',
                recommendations=''
            )
            db.session.add(visit_report)
        else:
            visit_report.meeting_held = meeting_held
            visit_report.attendance_percentage = attendance_percentage
            visit_report.report_content = meeting_notes
        
        # Process service fee
        service_fee_amount = int(request.form.get('service_fee_amount', 0))
        if service_fee_amount > 0:
            service_fee = ServiceFeeCollection(
                group_id=group_id,
                officer_id=officer_id,
                amount=service_fee_amount,
                collection_date=collection_date,
                notes=request.form.get('service_fee_notes', '')
            )
            db.session.add(service_fee)
        
        # Process registration fees
        project_reg_fee = int(request.form.get('project_reg_fee', 0))
        member_reg_fee = int(request.form.get('member_reg_fee', 0))
        if project_reg_fee > 0 or member_reg_fee > 0:
            registration = RegistrationFeeCollection(
                group_id=group_id,
                officer_id=officer_id,
                project_amount=project_reg_fee,
                member_amount=member_reg_fee,
                collection_date=collection_date,
                notes=request.form.get('registration_notes', '')
            )
            db.session.add(registration)
        
        # Process loan collection
        loan_amount = int(request.form.get('ukombozini_loan_amount', 0))
        if loan_amount > 0:
            loan_collection = LoanCollection(
                group_id=group_id,
                officer_id=officer_id,
                amount=loan_amount,
                payment_type=request.form.get('loan_payment_type', 'cash'),
                collection_date=collection_date,
                notes=request.form.get('loan_notes', '')
            )
            db.session.add(loan_collection)
        
        # Process project funds
        project_amount = int(request.form.get('ukombozini_project_amount', 0))
        if project_amount > 0:
            project_collection = ProjectFundCollection(
                group_id=group_id,
                officer_id=officer_id,
                amount=project_amount,
                project_type=request.form.get('project_type', 'other'),
                collection_date=collection_date,
                notes=request.form.get('project_notes', '')
            )
            db.session.add(project_collection)
        
        # Process welfare collection
        welfare_amount = int(request.form.get('welfare_amount', 0))
        if welfare_amount > 0:
            welfare_collection = WelfareCollection(
                group_id=group_id,
                officer_id=officer_id,
                amount=welfare_amount,
                purpose=request.form.get('welfare_purpose', 'general'),
                collection_date=collection_date,
                notes=request.form.get('welfare_notes', '')
            )
            db.session.add(welfare_collection)
        
        db.session.commit()
        
        # Check if the user wants to add another entry
        add_another = request.form.get('add_another') == 'true'
        
        # Return appropriate response
        if is_ajax:
            return jsonify({'success': True, 'visit_report_id': visit_report.id})
        
        flash('Collection data saved successfully!', 'success')
        if add_another:
            return redirect(url_for('field_officers_web.collection_entry'))
        else:
            return redirect(url_for('field_officers_web.collection_summary', date=collection_date.strftime('%Y-%m-%d')))
    
    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        
        flash(f'Error saving collection data: {str(e)}', 'danger')
        return redirect(url_for('field_officers_web.collection_entry'))

@bp.route('/api/dashboard-stats')
@login_required
def get_dashboard_stats():
    """API endpoint to get dashboard statistics for field officers"""
    try:
        # Get the current date and start of month
        current_date = datetime.now().date()
        start_of_month = current_date.replace(day=1)
        
        # Initialize stats
        stats = {
            'total_service_fees': 0,
            'total_loans': 0,
            'total_projects': 0,
            'total_welfare': 0,
            'total_registrations': 0,
            'total_collection': 0,
            'visit_count': 0,
            'group_count': 0,
            'recent_collections': []
        }
        
        # Filter based on current user role
        if current_user.role == 'admin':
            # For admin, get all collections
            officer_filter = True
        else:
            # For field officer, only get their collections
            officer_filter = ServiceFeeCollection.officer_id == current_user.id
            
        # Get service fees collected this month
        service_fees = ServiceFeeCollection.query.filter(
            ServiceFeeCollection.collection_date >= start_of_month,
            officer_filter
        ).all()
        
        stats['total_service_fees'] = sum(fee.amount for fee in service_fees)
        
        # Get loan collections this month
        loans = LoanCollection.query.filter(
            LoanCollection.collection_date >= start_of_month,
            officer_filter
        ).all()
        
        stats['total_loans'] = sum(loan.amount for loan in loans)
        
        # Get project funds this month
        projects = ProjectFundCollection.query.filter(
            ProjectFundCollection.collection_date >= start_of_month,
            officer_filter
        ).all()
        
        stats['total_projects'] = sum(project.amount for project in projects)
        
        # Get welfare collections this month
        welfare = WelfareCollection.query.filter(
            WelfareCollection.collection_date >= start_of_month,
            officer_filter
        ).all()
        
        stats['total_welfare'] = sum(welf.amount for welf in welfare)
        
        # Get registration fees this month
        registrations = RegistrationFeeCollection.query.filter(
            RegistrationFeeCollection.collection_date >= start_of_month,
            officer_filter
        ).all()
        
        stats['total_registrations'] = sum(reg.project_amount + reg.member_amount for reg in registrations)
        
        # Calculate total collection
        stats['total_collection'] = (
            stats['total_service_fees'] + 
            stats['total_loans'] + 
            stats['total_projects'] + 
            stats['total_welfare'] + 
            stats['total_registrations']
        )
        
        # Get visit count this month
        visit_filter = VisitReport.visit_date >= start_of_month
        if current_user.role != 'admin':
            visit_filter = and_(visit_filter, VisitReport.officer_id == current_user.id)
            
        stats['visit_count'] = VisitReport.query.filter(visit_filter).count()
        
        # Get count of unique groups visited this month
        unique_groups = db.session.query(VisitReport.group_id)\
            .filter(visit_filter)\
            .distinct()\
            .count()
            
        stats['group_count'] = unique_groups
        
        # Get 5 most recent collections
        recent_service_fees = ServiceFeeCollection.query.filter(officer_filter)\
            .order_by(ServiceFeeCollection.collection_date.desc())\
            .limit(5)\
            .all()
            
        for fee in recent_service_fees:
            group = Group.query.get(fee.group_id)
            officer = User.query.get(fee.officer_id)
            
            if group and officer:
                stats['recent_collections'].append({
                    'date': fee.collection_date.strftime('%Y-%m-%d'),
                    'group_name': group.name,
                    'officer_name': f"{officer.first_name} {officer.last_name}",
                    'amount': fee.amount,
                    'type': 'Service Fee'
                })
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 