from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import (
    AgricultureCollection, SchoolFeesCollection,
    AgriculturePayment, User, Group
)
from app import db
from datetime import datetime

bp = Blueprint('collections', __name__)

# Agriculture Collection Routes
@bp.route('/agriculture', methods=['GET'])
@login_required
def get_agriculture_collections():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = AgricultureCollection.query
    return jsonify(AgricultureCollection.to_collection_dict(
        query, page, per_page, 'collections.get_agriculture_collections'
    ))

@bp.route('/agriculture', methods=['POST'])
@login_required
def create_agriculture_collection():
    data = request.get_json()
    collection = AgricultureCollection(
        user_id=data.get('user_id', current_user.id),
        group_id=data['group_id'],
        product_type=data['product_type'],
        quantity=data['quantity'],
        unit=data['unit'],
        unit_price=data['unit_price'],
        total_amount=float(data['quantity']) * float(data['unit_price']),
        collection_date=datetime.utcnow(),
        status='pending',
        payment_status='unpaid',
        notes=data.get('notes')
    )
    db.session.add(collection)
    db.session.commit()
    return jsonify(collection.to_dict()), 201

@bp.route('/agriculture/<int:id>', methods=['GET'])
@login_required
def get_agriculture_collection(id):
    collection = AgricultureCollection.query.get_or_404(id)
    return jsonify(collection.to_dict())

@bp.route('/agriculture/<int:id>', methods=['PUT'])
@login_required
def update_agriculture_collection(id):
    collection = AgricultureCollection.query.get_or_404(id)
    data = request.get_json()
    
    collection.status = data.get('status', collection.status)
    collection.payment_status = data.get('payment_status', collection.payment_status)
    collection.notes = data.get('notes', collection.notes)
    
    db.session.commit()
    return jsonify(collection.to_dict())

@bp.route('/agriculture/<int:id>/payments', methods=['POST'])
@login_required
def add_agriculture_payment(id):
    collection = AgricultureCollection.query.get_or_404(id)
    data = request.get_json()
    
    payment = AgriculturePayment(
        collection_id=collection.id,
        amount=data['amount'],
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    db.session.add(payment)
    
    # Update collection payment status
    total_paid = sum(p.amount for p in collection.payments) + float(data['amount'])
    if total_paid >= collection.total_amount:
        collection.payment_status = 'paid'
    elif total_paid > 0:
        collection.payment_status = 'partial'
    
    db.session.commit()
    return jsonify(payment.to_dict()), 201

# School Fees Collection Routes
@bp.route('/school-fees', methods=['GET'])
@login_required
def get_school_fees_collections():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = SchoolFeesCollection.query
    return jsonify(SchoolFeesCollection.to_collection_dict(
        query, page, per_page, 'collections.get_school_fees_collections'
    ))

@bp.route('/school-fees', methods=['POST'])
@login_required
def create_school_fees_collection():
    data = request.get_json()
    collection = SchoolFeesCollection(
        user_id=data.get('user_id', current_user.id),
        group_id=data['group_id'],
        student_name=data['student_name'],
        school_name=data['school_name'],
        term=data['term'],
        year=data['year'],
        amount=data['amount'],
        payment_date=datetime.utcnow(),
        status='pending',
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    db.session.add(collection)
    db.session.commit()
    return jsonify(collection.to_dict()), 201

@bp.route('/school-fees/<int:id>', methods=['GET'])
@login_required
def get_school_fees_collection(id):
    collection = SchoolFeesCollection.query.get_or_404(id)
    return jsonify(collection.to_dict())

@bp.route('/school-fees/<int:id>', methods=['PUT'])
@login_required
def update_school_fees_collection(id):
    collection = SchoolFeesCollection.query.get_or_404(id)
    data = request.get_json()
    
    collection.status = data.get('status', collection.status)
    collection.payment_method = data.get('payment_method', collection.payment_method)
    collection.reference_number = data.get('reference_number', collection.reference_number)
    collection.notes = data.get('notes', collection.notes)
    
    db.session.commit()
    return jsonify(collection.to_dict()) 