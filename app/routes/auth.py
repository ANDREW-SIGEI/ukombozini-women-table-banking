from flask import Blueprint, request, jsonify, url_for, redirect, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models import User
from app import db
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
        
    data = request.form if request.form else request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        if request.content_type == 'application/json':
            return jsonify({'error': 'Username already exists'}), 400
        flash('Username already exists', 'danger')
        return redirect(url_for('auth.register'))
    
    if User.query.filter_by(email=data['email']).first():
        if request.content_type == 'application/json':
            return jsonify({'error': 'Email already registered'}), 400
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.register'))
    
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data.get('phone_number'),
        role=data.get('role', 'member')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    if request.content_type == 'application/json':
        return jsonify(user.to_dict()), 201
        
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form
        
    user = User.query.filter_by(username=data['username']).first()
    
    if user is None or not user.check_password(data['password']):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Invalid username or password'}), 401
        flash('Invalid username or password', 'danger')
        return redirect(url_for('auth.login'))
    
    remember_me = data.get('remember_me', False)
    if isinstance(remember_me, str) and remember_me.lower() == 'on':
        remember_me = True
        
    login_user(user, remember=remember_me)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.index')
    
    if request.content_type == 'application/json':
        # Create JWT token
        access_token = create_access_token(identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        return jsonify({
            'message': 'Logged in successfully',
            'access_token': access_token,
            'user': user.to_dict(),
            'next_page': next_page
        }), 200
        
    flash('Logged in successfully!', 'success')
    return redirect(next_page)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    if request.content_type == 'application/json':
        return jsonify({'message': 'Logged out successfully'}), 200
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.index'))

@bp.route('/user')
@login_required
def get_user():
    return jsonify(current_user.to_dict())

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'GET':
        return render_template('auth/reset_password_request.html')
        
    data = request.form if request.form else request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        # Send password reset email
        token = user.get_reset_password_token()
        # TODO: Implement email sending functionality
        if request.content_type == 'application/json':
            return jsonify({'message': 'Password reset instructions sent'}), 200
        flash('Password reset instructions sent to your email.', 'info')
        return redirect(url_for('auth.login'))
        
    if request.content_type == 'application/json':
        return jsonify({'error': 'Email not found'}), 404
    flash('Email not found', 'danger')
    return redirect(url_for('auth.reset_password_request'))

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        if request.content_type == 'application/json':
            return jsonify({'error': 'Invalid or expired token'}), 400
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    if request.method == 'GET':
        return render_template('auth/reset_password.html', token=token)
        
    data = request.form if request.form else request.get_json()
    user.set_password(data['password'])
    db.session.commit()
    
    if request.content_type == 'application/json':
        return jsonify({'message': 'Password reset successfully'}), 200
    flash('Password has been reset successfully. Please log in.', 'success')
    return redirect(url_for('auth.login')) 