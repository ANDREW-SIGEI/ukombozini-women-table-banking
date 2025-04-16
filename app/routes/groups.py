from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import User, Group

bp = Blueprint('groups', __name__)

@bp.route('/')
@login_required
def list_groups():
    """Display a list of all groups"""
    try:
        groups = []
        if Group:
            groups = Group.query.all()
        return render_template('groups/index.html', groups=groups)
    except Exception as e:
        flash(f'Error loading groups: {str(e)}', 'danger')
        return render_template('groups/index.html', groups=[])

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """Create a new group"""
    if request.method == 'GET':
        return render_template('groups/create.html')
    
    try:
        if request.method == 'POST':
            # Process form data to create a new group
            name = request.form.get('name')
            location = request.form.get('location')
            description = request.form.get('description')
            
            if not name:
                flash('Group name is required.', 'danger')
                return render_template('groups/create.html')
            
            # Check if group with this name already exists
            if Group and Group.query.filter_by(name=name).first():
                flash('A group with this name already exists.', 'danger')
                return render_template('groups/create.html')
            
            # Create and save the new group
            if Group:
                group = Group(
                    name=name,
                    location=location or '',
                    description=description or ''
                )
                db.session.add(group)
                db.session.commit()
                
                flash('Group created successfully!', 'success')
                return redirect(url_for('groups.list_groups'))
            else:
                flash('Group model not available.', 'danger')
                return render_template('groups/create.html')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating group: {str(e)}', 'danger')
        return render_template('groups/create.html')

@bp.route('/<int:id>')
@login_required
def view_group(id):
    """View details of a specific group"""
    try:
        group = None
        members = []
        
        if Group:
            group = Group.query.get_or_404(id)
            if hasattr(group, 'members'):
                members = group.members
                
        return render_template('groups/view.html', group=group, members=members)
    except Exception as e:
        flash(f'Error loading group: {str(e)}', 'danger')
        return redirect(url_for('groups.list_groups'))

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group(id):
    """Edit an existing group"""
    if not Group:
        flash('Group model not available.', 'danger')
        return redirect(url_for('groups.list_groups'))
    
    try:
        group = Group.query.get_or_404(id)
        
        if request.method == 'GET':
            return render_template('groups/edit.html', group=group)
        
        if request.method == 'POST':
            # Update group with form data
            name = request.form.get('name')
            location = request.form.get('location')
            description = request.form.get('description')
            
            if not name:
                flash('Group name is required.', 'danger')
                return render_template('groups/edit.html', group=group)
            
            # Check if another group with this name exists
            existing_group = Group.query.filter_by(name=name).first()
            if existing_group and existing_group.id != id:
                flash('Another group with this name already exists.', 'danger')
                return render_template('groups/edit.html', group=group)
            
            # Update group
            group.name = name
            group.location = location or ''
            group.description = description or ''
            
            db.session.commit()
            flash('Group updated successfully!', 'success')
            return redirect(url_for('groups.view_group', id=id))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating group: {str(e)}', 'danger')
        return redirect(url_for('groups.list_groups'))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_group(id):
    """Delete a group"""
    if not Group:
        flash('Group model not available.', 'danger')
        return redirect(url_for('groups.list_groups'))
    
    try:
        group = Group.query.get_or_404(id)
        db.session.delete(group)
        db.session.commit()
        flash('Group deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting group: {str(e)}', 'danger')
    
    return redirect(url_for('groups.list_groups')) 