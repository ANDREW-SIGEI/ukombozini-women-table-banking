from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import (
    Loan, GroupLoan, Saving, GroupSaving,
    LoanPayment, GroupLoanPayment, User, Group,
    DividendDistribution, DividendPayment,
    TableBankingTransaction, TableBankingAccount, TableBankingInterest
)
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.models.collections import ServiceFeeCollection, RegistrationFeeCollection, LoanCollection, ProjectFundCollection, WelfareCollection
import random
import json

bp = Blueprint('financial', __name__)

# Collection retrieval functions used by field_officers_web module
def get_service_fee(group_id, date):
    """Get service fee collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Try to get service fee from database
    service_fee = ServiceFeeCollection.query.filter(
        ServiceFeeCollection.group_id == group_id,
        func.date(ServiceFeeCollection.collection_date) == date
    ).first()
    
    if service_fee:
        return service_fee.amount
    
    # Return 0 if no data found
    return 0

def get_project_registration_fee(group_id, date):
    """Get project registration fees collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get registration fee from database
    reg_fee = RegistrationFeeCollection.query.filter(
        RegistrationFeeCollection.group_id == group_id,
        func.date(RegistrationFeeCollection.collection_date) == date
    ).first()
    
    if reg_fee:
        return reg_fee.project_amount
    
    return 0

def get_member_registration_fee(group_id, date):
    """Get member registration fees collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get registration fee from database
    reg_fee = RegistrationFeeCollection.query.filter(
        RegistrationFeeCollection.group_id == group_id,
        func.date(RegistrationFeeCollection.collection_date) == date
    ).first()
    
    if reg_fee:
        return reg_fee.member_amount
    
    return 0

def get_ukombozini_loans_collected(group_id, date):
    """Get Ukombozini loans collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get loan collection from database
    loan = LoanCollection.query.filter(
        LoanCollection.group_id == group_id,
        func.date(LoanCollection.collection_date) == date
    ).all()
    
    # Sum all loan collections for this group on this date
    return sum(l.amount for l in loan) if loan else 0

def get_ukombozini_project_funds(group_id, date):
    """Get Ukombozini project funds collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get project fund collection from database
    project_funds = ProjectFundCollection.query.filter(
        ProjectFundCollection.group_id == group_id,
        func.date(ProjectFundCollection.collection_date) == date
    ).all()
    
    # Sum all project fund collections for this group on this date
    return sum(p.amount for p in project_funds) if project_funds else 0

def get_group_welfare_collected(group_id, date):
    """Get welfare funds collected from a group on a specific date"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get welfare collection from database
    welfare = WelfareCollection.query.filter(
        WelfareCollection.group_id == group_id,
        func.date(WelfareCollection.collection_date) == date
    ).all()
    
    # Sum all welfare collections for this group on this date
    return sum(w.amount for w in welfare) if welfare else 0

# Loan Management Routes
@bp.route('/loans', methods=['GET'])
@login_required
def get_loans():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Loan.query
    return jsonify(Loan.to_collection_dict(
        query, page, per_page, 'financial.get_loans'
    ))

@bp.route('/loans', methods=['POST'])
@login_required
def create_loan():
    data = request.get_json()
    loan = Loan(
        user_id=current_user.id,
        amount=data['amount'],
        interest_rate=data['interest_rate'],
        term_months=data['term_months'],
        purpose=data.get('purpose'),
        status='pending'
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201

@bp.route('/loans/<int:id>', methods=['GET'])
@login_required
def get_loan(id):
    loan = Loan.query.get_or_404(id)
    return jsonify(loan.to_dict())

@bp.route('/loans/<int:id>/approve', methods=['POST'])
@login_required
def approve_loan(id):
    loan = Loan.query.get_or_404(id)
    loan.status = 'approved'
    loan.disbursement_date = datetime.utcnow()
    loan.due_date = datetime.utcnow()  # TODO: Calculate based on term
    db.session.commit()
    return jsonify(loan.to_dict())

@bp.route('/loans/<int:id>/payments', methods=['POST'])
@login_required
def add_loan_payment(id):
    loan = Loan.query.get_or_404(id)
    data = request.get_json()
    
    payment = LoanPayment(
        loan_id=loan.id,
        amount=data['amount'],
        payment_type=data.get('payment_type', 'cash'),
        reference_number=data.get('reference_number')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201

# Group Loan Routes
@bp.route('/group-loans', methods=['GET'])
@login_required
def get_group_loans():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = GroupLoan.query
    return jsonify(GroupLoan.to_collection_dict(
        query, page, per_page, 'financial.get_group_loans'
    ))

@bp.route('/group-loans', methods=['POST'])
@login_required
def create_group_loan():
    data = request.get_json()
    loan = GroupLoan(
        group_id=data['group_id'],
        amount=data['amount'],
        interest_rate=data['interest_rate'],
        term_months=data['term_months'],
        purpose=data.get('purpose'),
        status='pending'
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201

# Savings Management Routes
@bp.route('/savings', methods=['GET'])
@login_required
def get_savings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Saving.query.filter_by(user_id=current_user.id)
    return jsonify(Saving.to_collection_dict(
        query, page, per_page, 'financial.get_savings'
    ))

@bp.route('/savings', methods=['POST'])
@login_required
def create_saving():
    data = request.get_json()
    saving = Saving(
        user_id=current_user.id,
        amount=data['amount'],
        transaction_type=data['transaction_type'],
        description=data.get('description')
    )
    db.session.add(saving)
    db.session.commit()
    return jsonify(saving.to_dict()), 201

# Group Savings Routes
@bp.route('/group-savings', methods=['GET'])
@login_required
def get_group_savings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = GroupSaving.query
    return jsonify(GroupSaving.to_collection_dict(
        query, page, per_page, 'financial.get_group_savings'
    ))

@bp.route('/group-savings', methods=['POST'])
@login_required
def create_group_saving():
    data = request.get_json()
    saving = GroupSaving(
        group_id=data['group_id'],
        amount=data['amount'],
        transaction_type=data['transaction_type'],
        description=data.get('description')
    )
    db.session.add(saving)
    db.session.commit()
    return jsonify(saving.to_dict()), 201

# Dividend Management Routes
@bp.route('/dividends', methods=['GET'])
@login_required
def get_dividends():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = DividendDistribution.query
    return jsonify(DividendDistribution.to_collection_dict(
        query, page, per_page, 'financial.get_dividends'
    ))

@bp.route('/dividends', methods=['POST'])
@login_required
def create_dividend():
    data = request.get_json()
    distribution = DividendDistribution(
        group_id=data['group_id'],
        total_amount=data['total_amount'],
        distribution_date=datetime.utcnow(),
        distribution_type=data['distribution_type'],
        year=data['year'],
        period=data.get('period'),
        notes=data.get('notes')
    )
    db.session.add(distribution)
    db.session.commit()
    return jsonify(distribution.to_dict()), 201

@bp.route('/dividends/<int:id>/payments', methods=['POST'])
@login_required
def add_dividend_payment(id):
    distribution = DividendDistribution.query.get_or_404(id)
    data = request.get_json()
    
    payment = DividendPayment(
        distribution_id=distribution.id,
        user_id=data['user_id'],
        amount=data['amount'],
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201

@bp.route('/')
@login_required
def index():
    """Financial dashboard"""
    return render_template('financial/index.html')

@bp.route('/service-fees')
@login_required
def service_fees():
    """Service fees page"""
    return render_template('financial/service_fees.html')

@bp.route('/member-registrations')
@login_required
def member_registrations():
    """Member registration fees page"""
    return render_template('financial/member_registrations.html')

@bp.route('/project-registrations')
@login_required
def project_registrations():
    """Project registration fees page"""
    return render_template('financial/project_registrations.html')

@bp.route('/ukombozini-loans')
@login_required
def ukombozini_loans():
    """Ukombozini loans page"""
    return render_template('financial/ukombozini_loans.html')

@bp.route('/ukombozini-projects')
@login_required
def ukombozini_projects():
    """Ukombozini projects page"""
    return render_template('financial/ukombozini_projects.html')

@bp.route('/welfare')
@login_required
def welfare():
    """Welfare fees page"""
    return render_template('financial/welfare.html')

@bp.route('/tablebanking')
@login_required
def tablebanking():
    """Display tablebanking dashboard and summary"""
    # Get statistics
    total_balance = db.session.query(func.sum(TableBankingAccount.balance)).scalar() or 0
    
    # Transactions in the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_txns_count = TableBankingTransaction.query.filter(
        TableBankingTransaction.transaction_date >= thirty_days_ago
    ).count()
    
    # Member count
    member_count = TableBankingAccount.query.count()
    
    # Total interest accrued
    total_interest = db.session.query(func.sum(TableBankingInterest.amount)).scalar() or 0
    
    # Get recent transactions
    recent_transactions = TableBankingTransaction.query.order_by(
        TableBankingTransaction.transaction_date.desc()
    ).limit(10).all()
    
    return render_template(
        'financial/tablebanking.html',
        total_balance=total_balance,
        recent_txns_count=recent_txns_count,
        member_count=member_count,
        total_interest=total_interest,
        transactions=recent_transactions
    )

@bp.route('/tablebanking/transactions', methods=['GET'])
@login_required
def tablebanking_transactions():
    """List all tablebanking transactions with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    transaction_type = request.args.get('type')
    member_id = request.args.get('member_id', type=int)
    group_id = request.args.get('group_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Build query with filters
    query = TableBankingTransaction.query
    
    if transaction_type:
        query = query.filter(TableBankingTransaction.transaction_type == transaction_type)
    
    if member_id:
        query = query.filter(TableBankingTransaction.member_id == member_id)
    
    if group_id:
        query = query.filter(TableBankingTransaction.group_id == group_id)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(TableBankingTransaction.transaction_date >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(TableBankingTransaction.transaction_date <= to_date_obj)
        except ValueError:
            pass
    
    # Get paginated results
    pagination = query.order_by(TableBankingTransaction.transaction_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get members and groups for filter dropdowns
    members = User.query.filter_by(role='member').all()
    groups = Group.query.all()
    
    return render_template(
        'financial/tablebanking_transactions.html',
        transactions=pagination.items,
        pagination=pagination,
        members=members,
        groups=groups,
        transaction_type=transaction_type,
        member_id=member_id,
        group_id=group_id,
        from_date=from_date,
        to_date=to_date
    )

@bp.route('/tablebanking/deposit', methods=['GET', 'POST'])
@login_required
def tablebanking_deposit():
    """Handle tablebanking deposit"""
    if request.method == 'POST':
        member_id = request.form.get('member_id', type=int)
        group_id = request.form.get('group_id', type=int)
        amount = request.form.get('amount', type=float)
        transaction_date_str = request.form.get('transaction_date')
        notes = request.form.get('notes', '')
        
        if not member_id or not amount or amount <= 0:
            flash('Member and amount are required fields.', 'danger')
            members = User.query.filter_by(role='member').all()
            groups = Group.query.all()
            return render_template('financial/tablebanking_deposit.html', members=members, groups=groups)
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date() if transaction_date_str else datetime.now().date()
            
            # Create transaction
            transaction = TableBankingTransaction(
                member_id=member_id,
                group_id=group_id,
                amount=amount,
                transaction_type='deposit',
                transaction_date=transaction_date,
                notes=notes,
                recorded_by=current_user.id
            )
            
            db.session.add(transaction)
            
            # Update member account balance
            account = TableBankingAccount.query.filter_by(member_id=member_id).first()
            
            if not account:
                account = TableBankingAccount(
                    member_id=member_id,
                    balance=amount,
                    last_transaction_date=transaction_date
                )
                db.session.add(account)
            else:
                account.balance += amount
                account.last_transaction_date = transaction_date
            
            db.session.commit()
            flash('Deposit recorded successfully!', 'success')
            return redirect(url_for('financial.tablebanking_transactions'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing deposit: {str(e)}', 'danger')
    
    # GET request - display form
    members = User.query.filter_by(role='member').all()
    groups = Group.query.all()
    return render_template(
        'financial/tablebanking_deposit.html',
        members=members,
        groups=groups,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/tablebanking/withdrawal', methods=['GET', 'POST'])
@login_required
def tablebanking_withdrawal():
    """Handle tablebanking withdrawal"""
    if request.method == 'POST':
        member_id = request.form.get('member_id', type=int)
        group_id = request.form.get('group_id', type=int)
        amount = request.form.get('amount', type=float)
        transaction_date_str = request.form.get('transaction_date')
        notes = request.form.get('notes', '')
        
        if not member_id or not amount or amount <= 0:
            flash('Member and amount are required fields.', 'danger')
            members = User.query.filter_by(role='member').all()
            groups = Group.query.all()
            return render_template('financial/tablebanking_withdrawal.html', members=members, groups=groups)
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date() if transaction_date_str else datetime.now().date()
            
            # Check if member has sufficient balance
            account = TableBankingAccount.query.filter_by(member_id=member_id).first()
            
            if not account or account.balance < amount:
                flash('Insufficient balance for this withdrawal.', 'danger')
                members = User.query.filter_by(role='member').all()
                groups = Group.query.all()
                return render_template('financial/tablebanking_withdrawal.html', members=members, groups=groups)
            
            # Create transaction
            transaction = TableBankingTransaction(
                member_id=member_id,
                group_id=group_id,
                amount=amount,
                transaction_type='withdrawal',
                transaction_date=transaction_date,
                notes=notes,
                recorded_by=current_user.id
            )
            
            db.session.add(transaction)
            
            # Update member account balance
            account.balance -= amount
            account.last_transaction_date = transaction_date
            
            db.session.commit()
            flash('Withdrawal processed successfully!', 'success')
            return redirect(url_for('financial.tablebanking_transactions'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing withdrawal: {str(e)}', 'danger')
    
    # GET request - display form
    members = User.query.filter_by(role='member').all()
    groups = Group.query.all()
    return render_template(
        'financial/tablebanking_withdrawal.html',
        members=members,
        groups=groups,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/tablebanking/interest', methods=['GET', 'POST'])
@login_required
def tablebanking_interest():
    """Calculate and apply interest to tablebanking accounts"""
    if request.method == 'POST':
        rate = request.form.get('interest_rate', type=float)
        date_str = request.form.get('application_date')
        notes = request.form.get('notes', '')
        
        if not rate or rate <= 0:
            flash('Please enter a valid interest rate.', 'danger')
            return render_template('financial/tablebanking_interest.html')
        
        try:
            application_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
            
            # Get all accounts with positive balance
            accounts = TableBankingAccount.query.filter(TableBankingAccount.balance > 0).all()
            
            interest_records = []
            
            for account in accounts:
                # Calculate interest amount
                interest_amount = account.balance * (rate / 100)
                
                # Create interest record
                interest = TableBankingInterest(
                    member_id=account.member_id,
                    amount=interest_amount,
                    rate=rate,
                    application_date=application_date,
                    notes=notes
                )
                
                interest_records.append(interest)
                db.session.add(interest)
                
                # Update account balance
                account.balance += interest_amount
                
                # Create transaction record
                transaction = TableBankingTransaction(
                    member_id=account.member_id,
                    amount=interest_amount,
                    transaction_type='interest',
                    transaction_date=application_date,
                    notes=f'Interest applied at {rate}% rate',
                    recorded_by=current_user.id
                )
                
                db.session.add(transaction)
            
            db.session.commit()
            flash(f'Interest applied successfully to {len(interest_records)} accounts!', 'success')
            return redirect(url_for('financial.tablebanking'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error applying interest: {str(e)}', 'danger')
    
    # GET request - display form
    return render_template('financial/tablebanking_interest.html', today=datetime.now().strftime('%Y-%m-%d'))

@bp.route('/tablebanking/members')
@login_required
def tablebanking_members():
    """Display all members with their tablebanking accounts"""
    accounts = db.session.query(
        TableBankingAccount,
        User,
        func.sum(TableBankingTransaction.amount).filter(TableBankingTransaction.transaction_type == 'deposit').label('total_deposits'),
        func.sum(TableBankingTransaction.amount).filter(TableBankingTransaction.transaction_type == 'withdrawal').label('total_withdrawals'),
        func.sum(TableBankingInterest.amount).label('total_interest')
    ).join(
        User, User.id == TableBankingAccount.member_id
    ).outerjoin(
        TableBankingTransaction, TableBankingTransaction.member_id == TableBankingAccount.member_id
    ).outerjoin(
        TableBankingInterest, TableBankingInterest.member_id == TableBankingAccount.member_id
    ).group_by(
        TableBankingAccount.id
    ).all()
    
    return render_template('financial/tablebanking_members.html', accounts=accounts)

@bp.route('/tablebanking/reports')
@login_required
def tablebanking_reports():
    """Generate tablebanking reports"""
    report_type = request.args.get('type', 'summary')
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else (datetime.now() - timedelta(days=30)).date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else datetime.now().date()
        
        # Default to last 30 days if no dates provided
        if not from_date_str and not to_date_str:
            from_date = (datetime.now() - timedelta(days=30)).date()
            to_date = datetime.now().date()
        
        if report_type == 'summary':
            # Get summary statistics
            total_deposits = db.session.query(
                func.sum(TableBankingTransaction.amount)
            ).filter(
                TableBankingTransaction.transaction_type == 'deposit',
                TableBankingTransaction.transaction_date >= from_date,
                TableBankingTransaction.transaction_date <= to_date
            ).scalar() or 0
            
            total_withdrawals = db.session.query(
                func.sum(TableBankingTransaction.amount)
            ).filter(
                TableBankingTransaction.transaction_type == 'withdrawal',
                TableBankingTransaction.transaction_date >= from_date,
                TableBankingTransaction.transaction_date <= to_date
            ).scalar() or 0
            
            total_interest = db.session.query(
                func.sum(TableBankingInterest.amount)
            ).filter(
                TableBankingInterest.application_date >= from_date,
                TableBankingInterest.application_date <= to_date
            ).scalar() or 0
            
            transaction_count = TableBankingTransaction.query.filter(
                TableBankingTransaction.transaction_date >= from_date,
                TableBankingTransaction.transaction_date <= to_date
            ).count()
            
            # Get daily transaction totals for chart
            daily_totals = db.session.query(
                func.date(TableBankingTransaction.transaction_date).label('date'),
                func.sum(TableBankingTransaction.amount).filter(TableBankingTransaction.transaction_type == 'deposit').label('deposits'),
                func.sum(TableBankingTransaction.amount).filter(TableBankingTransaction.transaction_type == 'withdrawal').label('withdrawals')
            ).filter(
                TableBankingTransaction.transaction_date >= from_date,
                TableBankingTransaction.transaction_date <= to_date
            ).group_by(
                func.date(TableBankingTransaction.transaction_date)
            ).all()
            
            chart_dates = [str(row.date) for row in daily_totals]
            chart_deposits = [float(row.deposits or 0) for row in daily_totals]
            chart_withdrawals = [float(row.withdrawals or 0) for row in daily_totals]
            
            return render_template(
                'financial/tablebanking_report_summary.html',
                total_deposits=total_deposits,
                total_withdrawals=total_withdrawals,
                total_interest=total_interest,
                transaction_count=transaction_count,
                from_date=from_date,
                to_date=to_date,
                chart_dates=json.dumps(chart_dates),
                chart_deposits=json.dumps(chart_deposits),
                chart_withdrawals=json.dumps(chart_withdrawals)
            )
            
        elif report_type == 'transactions':
            # Get all transactions in date range
            transactions = TableBankingTransaction.query.filter(
                TableBankingTransaction.transaction_date >= from_date,
                TableBankingTransaction.transaction_date <= to_date
            ).order_by(
                TableBankingTransaction.transaction_date.desc()
            ).all()
            
            return render_template(
                'financial/tablebanking_report_transactions.html',
                transactions=transactions,
                from_date=from_date,
                to_date=to_date
            )
            
        elif report_type == 'members':
            # Get member statistics
            member_stats = db.session.query(
                User,
                TableBankingAccount,
                func.sum(TableBankingTransaction.amount).filter(
                    TableBankingTransaction.transaction_type == 'deposit',
                    TableBankingTransaction.transaction_date >= from_date,
                    TableBankingTransaction.transaction_date <= to_date
                ).label('period_deposits'),
                func.sum(TableBankingTransaction.amount).filter(
                    TableBankingTransaction.transaction_type == 'withdrawal',
                    TableBankingTransaction.transaction_date >= from_date,
                    TableBankingTransaction.transaction_date <= to_date
                ).label('period_withdrawals')
            ).join(
                TableBankingAccount, User.id == TableBankingAccount.member_id
            ).outerjoin(
                TableBankingTransaction, User.id == TableBankingTransaction.member_id
            ).filter(
                User.role == 'member'
            ).group_by(
                User.id
            ).all()
            
            return render_template(
                'financial/tablebanking_report_members.html',
                member_stats=member_stats,
                from_date=from_date,
                to_date=to_date
            )
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
    
    # Default report selection page
    return render_template('financial/tablebanking_reports.html')

@bp.route('/api/tablebanking/member/<int:member_id>/balance')
@login_required
def get_member_balance(member_id):
    """API endpoint to get a member's current balance"""
    account = TableBankingAccount.query.filter_by(member_id=member_id).first()
    
    if account:
        return jsonify({
            'success': True,
            'balance': account.balance,
            'last_transaction_date': account.last_transaction_date.strftime('%Y-%m-%d') if account.last_transaction_date else None
        })
    else:
        return jsonify({
            'success': False,
            'balance': 0,
            'message': 'No account found for this member'
        })

# Add routes for savings and loans
@bp.route('/savings')
@login_required
def savings():
    return render_template('financial/savings.html')

@bp.route('/loans')
@login_required
def loans():
    return render_template('financial/loans.html')

@bp.route('/loan-collections')
@login_required
def loan_collections():
    return render_template('financial/loan_collections.html')

@bp.route('/record-loan-collection', methods=['POST'])
@login_required
def record_loan_collection():
    """Handle recording a new loan collection"""
    if request.method == 'POST':
        try:
            collection_type = request.form.get('collection_type')
            amount = request.form.get('amount', type=float)
            collection_date_str = request.form.get('collection_date')
            payment_method = request.form.get('payment_method')
            reference_number = request.form.get('reference_number', '')
            notes = request.form.get('notes', '')
            
            # Validate required fields
            if not collection_type or not amount or not collection_date_str or not payment_method:
                flash('All required fields must be completed.', 'danger')
                return redirect(url_for('financial.loan_collections'))
            
            collection_date = datetime.strptime(collection_date_str, '%Y-%m-%d').date()
            
            # Process based on collection type
            if collection_type == 'group':
                group_id = request.form.get('group_id', type=int)
                group_loan_id = request.form.get('group_loan_id', type=int)
                
                if not group_id or not group_loan_id:
                    flash('Group and loan must be selected for group collections.', 'danger')
                    return redirect(url_for('financial.loan_collections'))
                
                # Create group loan collection record
                collection = LoanCollection(
                    group_id=group_id,
                    loan_id=group_loan_id,
                    amount=amount,
                    collection_date=collection_date,
                    payment_method=payment_method,
                    reference_number=reference_number,
                    notes=notes,
                    recorded_by=current_user.id
                )
                
            elif collection_type == 'individual':
                member_id = request.form.get('member_id', type=int)
                loan_id = request.form.get('loan_id', type=int)
                
                if not member_id or not loan_id:
                    flash('Member and loan must be selected for individual collections.', 'danger')
                    return redirect(url_for('financial.loan_collections'))
                
                # Create individual loan collection record
                collection = LoanCollection(
                    member_id=member_id,
                    loan_id=loan_id,
                    amount=amount,
                    collection_date=collection_date,
                    payment_method=payment_method,
                    reference_number=reference_number,
                    notes=notes,
                    recorded_by=current_user.id
                )
            
            else:
                flash('Invalid collection type.', 'danger')
                return redirect(url_for('financial.loan_collections'))
            
            db.session.add(collection)
            db.session.commit()
            
            flash('Loan collection recorded successfully!', 'success')
            return redirect(url_for('financial.loan_collections'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording collection: {str(e)}', 'danger')
    
    return redirect(url_for('financial.loan_collections')) 