from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import (
    Group, GroupMembership, User, Loan, GroupLoan,
    Saving, GroupSaving, AgricultureCollection,
    SchoolFeesCollection
)
from app import db
from datetime import datetime

bp = Blueprint('api', __name__)

# Group Management Routes
@bp.route('/groups', methods=['GET'])
@login_required
def get_groups():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Group.query
    return jsonify(Group.to_collection_dict(
        query, page, per_page, 'api.get_groups'
    ))

@bp.route('/groups', methods=['POST'])
@login_required
def create_group():
    data = request.get_json()
    group = Group(
        name=data['name'],
        registration_number=data['registration_number'],
        location=data['location'],
        description=data.get('description'),
        meeting_schedule=data.get('meeting_schedule'),
        status='active'
    )
    db.session.add(group)
    
    # Add creator as group member with chairperson role
    membership = GroupMembership(
        user_id=current_user.id,
        group_id=group.id,
        role='chairperson',
        join_date=datetime.utcnow(),
        status='active'
    )
    db.session.add(membership)
    
    db.session.commit()
    return jsonify(group.to_dict()), 201

@bp.route('/groups/<int:id>', methods=['GET'])
@login_required
def get_group(id):
    group = Group.query.get_or_404(id)
    return jsonify(group.to_dict())

@bp.route('/groups/<int:id>', methods=['PUT'])
@login_required
def update_group(id):
    group = Group.query.get_or_404(id)
    data = request.get_json()
    
    group.name = data.get('name', group.name)
    group.location = data.get('location', group.location)
    group.description = data.get('description', group.description)
    group.meeting_schedule = data.get('meeting_schedule', group.meeting_schedule)
    group.status = data.get('status', group.status)
    
    db.session.commit()
    return jsonify(group.to_dict())

@bp.route('/groups/<int:id>/members', methods=['GET'])
@login_required
def get_group_members(id):
    group = Group.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    members = GroupMembership.query.filter_by(group_id=id)
    return jsonify([{
        **member.to_dict(),
        'user': User.query.get(member.user_id).to_dict()
    } for member in members])

@bp.route('/groups/<int:id>/members', methods=['POST'])
@login_required
def add_group_member(id):
    group = Group.query.get_or_404(id)
    data = request.get_json()
    
    user = User.query.get_or_404(data['user_id'])
    if GroupMembership.query.filter_by(
        user_id=user.id, group_id=group.id
    ).first():
        return jsonify({'error': 'User is already a member'}), 400
    
    membership = GroupMembership(
        user_id=user.id,
        group_id=group.id,
        role=data.get('role', 'member'),
        join_date=datetime.utcnow(),
        status='active'
    )
    db.session.add(membership)
    db.session.commit()
    
    return jsonify(membership.to_dict()), 201

# Member Management Routes
@bp.route('/members', methods=['GET'])
@login_required
def get_members():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = User.query.filter_by(role='member')
    return jsonify(User.to_collection_dict(
        query, page, per_page, 'api.get_members'
    ))

@bp.route('/members/<int:id>', methods=['GET'])
@login_required
def get_member(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@bp.route('/members/<int:id>', methods=['PUT'])
@login_required
def update_member(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.email = data.get('email', user.email)
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/members/<int:id>/groups', methods=['GET'])
@login_required
def get_member_groups(id):
    user = User.query.get_or_404(id)
    memberships = GroupMembership.query.filter_by(user_id=id)
    return jsonify([{
        **membership.to_dict(),
        'group': Group.query.get(membership.group_id).to_dict()
    } for membership in memberships])

@bp.route('/members/<int:id>/loans', methods=['GET'])
@login_required
def get_member_loans(id):
    user = User.query.get_or_404(id)
    loans = Loan.query.filter_by(user_id=id)
    return jsonify([loan.to_dict() for loan in loans])

@bp.route('/members/<int:id>/savings', methods=['GET'])
@login_required
def get_member_savings(id):
    user = User.query.get_or_404(id)
    savings = Saving.query.filter_by(user_id=id)
    return jsonify([saving.to_dict() for saving in savings]) 