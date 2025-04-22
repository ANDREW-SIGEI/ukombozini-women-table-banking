from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import (
    AccountingTransaction, User, Group, Loan,
    GroupLoan, Saving, GroupSaving
)
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('accounting', __name__)

# Accounting Transaction Routes
@bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = AccountingTransaction.query
    
    # Filter by date range if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        query = query.filter(
            AccountingTransaction.transaction_date.between(start_date, end_date)
        )
    
    # Filter by category if provided
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    
    return jsonify(AccountingTransaction.to_collection_dict(
        query, page, per_page, 'accounting.get_transactions'
    ))

@bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    data = request.get_json()
    transaction = AccountingTransaction(
        transaction_type=data['transaction_type'],
        amount=data['amount'],
        description=data.get('description'),
        category=data['category'],
        transaction_date=datetime.utcnow(),
        reference_number=data.get('reference_number'),
        payment_method=data.get('payment_method', 'cash'),
        status='pending',
        notes=data.get('notes'),
        user_id=data.get('user_id'),
        group_id=data.get('group_id')
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict()), 201

@bp.route('/transactions/<int:id>', methods=['GET'])
@login_required
def get_transaction(id):
    transaction = AccountingTransaction.query.get_or_404(id)
    return jsonify(transaction.to_dict())

# Reports Routes
@bp.route('/reports/summary', methods=['GET'])
@login_required
def get_summary_report():
    # Get total loans
    total_individual_loans = db.session.query(
        func.count(Loan.id),
        func.sum(Loan.amount)
    ).first()
    
    total_group_loans = db.session.query(
        func.count(GroupLoan.id),
        func.sum(GroupLoan.amount)
    ).first()
    
    # Get total savings
    total_individual_savings = db.session.query(
        func.count(Saving.id),
        func.sum(Saving.amount)
    ).filter_by(transaction_type='deposit').first()
    
    total_group_savings = db.session.query(
        func.count(GroupSaving.id),
        func.sum(GroupSaving.amount)
    ).filter_by(transaction_type='deposit').first()
    
    return jsonify({
        'loans': {
            'individual': {
                'count': total_individual_loans[0] or 0,
                'amount': float(total_individual_loans[1] or 0)
            },
            'group': {
                'count': total_group_loans[0] or 0,
                'amount': float(total_group_loans[1] or 0)
            }
        },
        'savings': {
            'individual': {
                'count': total_individual_savings[0] or 0,
                'amount': float(total_individual_savings[1] or 0)
            },
            'group': {
                'count': total_group_savings[0] or 0,
                'amount': float(total_group_savings[1] or 0)
            }
        }
    })

@bp.route('/reports/transactions', methods=['GET'])
@login_required
def get_transaction_report():
    start_date = request.args.get('start_date', 
        (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', 
        datetime.utcnow().strftime('%Y-%m-%d'))
    
    # Get transactions by category
    transactions_by_category = db.session.query(
        AccountingTransaction.category,
        func.count(AccountingTransaction.id),
        func.sum(AccountingTransaction.amount)
    ).filter(
        AccountingTransaction.transaction_date.between(start_date, end_date)
    ).group_by(AccountingTransaction.category).all()
    
    # Get transactions by type
    transactions_by_type = db.session.query(
        AccountingTransaction.transaction_type,
        func.count(AccountingTransaction.id),
        func.sum(AccountingTransaction.amount)
    ).filter(
        AccountingTransaction.transaction_date.between(start_date, end_date)
    ).group_by(AccountingTransaction.transaction_type).all()
    
    return jsonify({
        'by_category': [{
            'category': cat,
            'count': count,
            'amount': float(amount or 0)
        } for cat, count, amount in transactions_by_category],
        'by_type': [{
            'type': type_,
            'count': count,
            'amount': float(amount or 0)
        } for type_, count, amount in transactions_by_type]
    })

@bp.route('/reports/loans', methods=['GET'])
@login_required
def get_loan_report():
    # Get loans by status
    loans_by_status = db.session.query(
        Loan.status,
        func.count(Loan.id),
        func.sum(Loan.amount)
    ).group_by(Loan.status).all()
    
    # Get group loans by status
    group_loans_by_status = db.session.query(
        GroupLoan.status,
        func.count(GroupLoan.id),
        func.sum(GroupLoan.amount)
    ).group_by(GroupLoan.status).all()
    
    return jsonify({
        'individual_loans': [{
            'status': status,
            'count': count,
            'amount': float(amount or 0)
        } for status, count, amount in loans_by_status],
        'group_loans': [{
            'status': status,
            'count': count,
            'amount': float(amount or 0)
        } for status, count, amount in group_loans_by_status]
    }) 