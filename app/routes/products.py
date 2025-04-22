from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.products import LoanProduct, SavingProduct
from app import db

products_bp = Blueprint('products', __name__)
bp = products_bp

@products_bp.route('/loan-products', methods=['GET'])
@jwt_required()
def get_loan_products():
    products = LoanProduct.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'interest_rate': p.interest_rate,
        'min_amount': p.min_amount,
        'max_amount': p.max_amount,
        'min_term': p.min_term,
        'max_term': p.max_term
    } for p in products])

@products_bp.route('/loan-products/<int:id>', methods=['GET'])
@jwt_required()
def get_loan_product(id):
    product = LoanProduct.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'interest_rate': product.interest_rate,
        'min_amount': product.min_amount,
        'max_amount': product.max_amount,
        'min_term': product.min_term,
        'max_term': product.max_term,
        'is_active': product.is_active,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    })

@products_bp.route('/saving-products', methods=['GET'])
@jwt_required()
def get_saving_products():
    products = SavingProduct.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'interest_rate': p.interest_rate,
        'min_balance': p.min_balance,
        'withdrawal_fee': p.withdrawal_fee
    } for p in products])

@products_bp.route('/saving-products/<int:id>', methods=['GET'])
@jwt_required()
def get_saving_product(id):
    product = SavingProduct.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'interest_rate': product.interest_rate,
        'min_balance': product.min_balance,
        'withdrawal_fee': product.withdrawal_fee,
        'is_active': product.is_active,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    })

@products_bp.route('/loan-products', methods=['POST'])
@jwt_required()
def create_loan_product():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    product = LoanProduct(
        name=data['name'],
        description=data.get('description'),
        interest_rate=data['interest_rate'],
        min_amount=data['min_amount'],
        max_amount=data['max_amount'],
        min_term=data['min_term'],
        max_term=data['max_term']
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Loan product created successfully', 'id': product.id}), 201

@products_bp.route('/loan-products/<int:id>', methods=['PUT'])
@jwt_required()
def update_loan_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = LoanProduct.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.interest_rate = data.get('interest_rate', product.interest_rate)
    product.min_amount = data.get('min_amount', product.min_amount)
    product.max_amount = data.get('max_amount', product.max_amount)
    product.min_term = data.get('min_term', product.min_term)
    product.max_term = data.get('max_term', product.max_term)
    product.is_active = data.get('is_active', product.is_active)
    
    db.session.commit()
    return jsonify({'message': 'Loan product updated successfully', 'id': product.id})

@products_bp.route('/loan-products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_loan_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = LoanProduct.query.get_or_404(id)
    
    # Soft delete by setting is_active to False
    product.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Loan product deleted successfully'})

@products_bp.route('/saving-products', methods=['POST'])
@jwt_required()
def create_saving_product():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    product = SavingProduct(
        name=data['name'],
        description=data.get('description'),
        interest_rate=data['interest_rate'],
        min_balance=data['min_balance'],
        withdrawal_fee=data.get('withdrawal_fee', 0.0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Saving product created successfully', 'id': product.id}), 201

@products_bp.route('/saving-products/<int:id>', methods=['PUT'])
@jwt_required()
def update_saving_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = SavingProduct.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.interest_rate = data.get('interest_rate', product.interest_rate)
    product.min_balance = data.get('min_balance', product.min_balance)
    product.withdrawal_fee = data.get('withdrawal_fee', product.withdrawal_fee)
    product.is_active = data.get('is_active', product.is_active)
    
    db.session.commit()
    return jsonify({'message': 'Saving product updated successfully', 'id': product.id})

@products_bp.route('/saving-products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_saving_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = SavingProduct.query.get_or_404(id)
    
    # Soft delete by setting is_active to False
    product.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Saving product deleted successfully'}) 