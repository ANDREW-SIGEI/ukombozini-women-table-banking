from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models import SystemSetting
from app import db
from app.utils.auth import admin_required

bp = Blueprint('settings', __name__)

@bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    settings = SystemSetting.query.all()
    return jsonify([setting.to_dict() for setting in settings])

@bp.route('/settings/<string:key>', methods=['GET'])
@login_required
def get_setting(key):
    setting = SystemSetting.query.filter_by(key=key).first_or_404()
    return jsonify(setting.to_dict())

@bp.route('/settings', methods=['POST'])
@login_required
@admin_required
def create_setting():
    data = request.get_json()
    setting = SystemSetting(
        key=data['key'],
        value=data['value'],
        description=data.get('description'),
        type=data.get('type', 'string'),
        category=data.get('category', 'general')
    )
    db.session.add(setting)
    db.session.commit()
    return jsonify(setting.to_dict()), 201

@bp.route('/settings/<string:key>', methods=['PUT'])
@login_required
@admin_required
def update_setting(key):
    setting = SystemSetting.query.filter_by(key=key).first_or_404()
    data = request.get_json()
    
    setting.value = data.get('value', setting.value)
    setting.description = data.get('description', setting.description)
    setting.type = data.get('type', setting.type)
    setting.category = data.get('category', setting.category)
    
    db.session.commit()
    return jsonify(setting.to_dict())

@bp.route('/settings/categories', methods=['GET'])
@login_required
def get_setting_categories():
    categories = db.session.query(SystemSetting.category).distinct().all()
    return jsonify([category[0] for category in categories])

# Default settings initialization
def init_default_settings():
    """Initialize default system settings if they don't exist."""
    # This would normally query the database and initialize settings
    # For now, we'll just pass since this is a placeholder
    pass

@bp.route('/')
def list():
    return jsonify({'message': 'Settings list'}) 