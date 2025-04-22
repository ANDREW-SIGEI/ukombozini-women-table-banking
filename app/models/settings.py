from app import db
from datetime import datetime
from .base import Model, TimestampMixin

class SystemSetting(Model, TimestampMixin):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(64), unique=True, nullable=False)
    setting_value = db.Column(db.String(512))
    description = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<SystemSetting {self.setting_key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 