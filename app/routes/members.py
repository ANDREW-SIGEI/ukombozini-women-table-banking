from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Group, GroupMembership
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('members', __name__)

@bp.route('/')
@login_required
def list_members():
    """Display a list of all members"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    
    # Query with search if provided
    query = User.query.filter_by(role='member')
    
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
    members = pagination.items
    
    # Prepare pagination links
    next_url = url_for('members.list_members', page=pagination.next_num, search=search) if pagination.has_next else None
    prev_url = url_for('members.list_members', page=pagination.prev_num, search=search) if pagination.has_prev else None
    
    return render_template(
        'members/index.html',
        members=members,
        page=page,
        total_pages=pagination.pages,
        next_url=next_url,
        prev_url=prev_url,
        search=search
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_member():
    """Create a new member"""
    groups = Group.query.all()
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        group_id = request.form.get('group_id')
        role_in_group = request.form.get('role_in_group', 'member')
        
        # Validation
        if not username or not email or not password:
            flash('Username, email and password are required fields', 'danger')
            return render_template('members/create.html', groups=groups)
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('members/create.html', groups=groups)
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('members/create.html', groups=groups)
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='member',
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user ID without committing
            
            # Add user to group if provided
            if group_id:
                group_membership = GroupMembership(
                    user_id=user.id,
                    group_id=int(group_id),
                    role=role_in_group,
                    join_date=datetime.utcnow(),
                    status='active'
                )
                db.session.add(group_membership)
            
            db.session.commit()
            flash('Member created successfully', 'success')
            return redirect(url_for('members.list_members'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating member: {str(e)}', 'danger')
            return render_template('members/create.html', groups=groups)
    
    return render_template('members/create.html', groups=groups)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view_member(id):
    """View a member's details"""
    member = User.query.filter_by(id=id, role='member').first_or_404()
    memberships = GroupMembership.query.filter_by(user_id=id).all()
    return render_template('members/view.html', member=member, memberships=memberships)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    """Edit a member's details"""
    member = User.query.filter_by(id=id, role='member').first_or_404()
    groups = Group.query.all()
    memberships = GroupMembership.query.filter_by(user_id=id).all()
    
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
            return render_template('members/edit.html', member=member, groups=groups, memberships=memberships)
        
        # Check if username already exists for different user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:
            flash('Username already exists', 'danger')
            return render_template('members/edit.html', member=member, groups=groups, memberships=memberships)
        
        # Check if email already exists for different user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != id:
            flash('Email already exists', 'danger')
            return render_template('members/edit.html', member=member, groups=groups, memberships=memberships)
        
        try:
            # Update member
            member.username = username
            member.email = email
            member.first_name = first_name
            member.last_name = last_name
            member.phone_number = phone_number
            member.is_active = is_active
            
            # Update password if provided
            if new_password:
                member.set_password(new_password)
            
            db.session.commit()
            flash('Member updated successfully', 'success')
            return redirect(url_for('members.view_member', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating member: {str(e)}', 'danger')
            return render_template('members/edit.html', member=member, groups=groups, memberships=memberships)
    
    return render_template('members/edit.html', member=member, groups=groups, memberships=memberships)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_member(id):
    """Delete a member"""
    member = User.query.filter_by(id=id, role='member').first_or_404()
    
    try:
        # Delete all group memberships
        GroupMembership.query.filter_by(user_id=id).delete()
        
        # Delete the user
        db.session.delete(member)
        db.session.commit()
        
        flash('Member deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting member: {str(e)}', 'danger')
    
    return redirect(url_for('members.list_members'))

@bp.route('/<int:id>/add-to-group', methods=['POST'])
@login_required
def add_to_group(id):
    """Add a member to a group"""
    member = User.query.filter_by(id=id, role='member').first_or_404()
    
    group_id = request.form.get('group_id')
    role = request.form.get('role', 'member')
    
    if not group_id:
        flash('Group is required', 'danger')
        return redirect(url_for('members.view_member', id=id))
    
    # Check if already in group
    existing = GroupMembership.query.filter_by(user_id=id, group_id=group_id).first()
    if existing:
        flash('Member is already in this group', 'warning')
        return redirect(url_for('members.view_member', id=id))
    
    try:
        membership = GroupMembership(
            user_id=id,
            group_id=int(group_id),
            role=role,
            join_date=datetime.utcnow(),
            status='active'
        )
        db.session.add(membership)
        db.session.commit()
        
        flash('Member added to group successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding member to group: {str(e)}', 'danger')
    
    return redirect(url_for('members.view_member', id=id))

@bp.route('/group-membership/<int:id>/remove', methods=['POST'])
@login_required
def remove_from_group(id):
    """Remove a member from a group"""
    membership = GroupMembership.query.get_or_404(id)
    member_id = membership.user_id
    
    try:
        db.session.delete(membership)
        db.session.commit()
        flash('Member removed from group successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing member from group: {str(e)}', 'danger')
    
    return redirect(url_for('members.view_member', id=member_id)) 