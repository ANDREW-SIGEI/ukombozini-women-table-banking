from app import db
from .base import Model, TimestampMixin, PaginatedAPIMixin

class Group(Model, TimestampMixin, PaginatedAPIMixin):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    registration_number = db.Column(db.String(64), unique=True)
    location = db.Column(db.String(128))
    description = db.Column(db.Text)
    meeting_schedule = db.Column(db.String(128))
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    
    # Relationships
    members = db.relationship('GroupMembership', back_populates='group')
    loans = db.relationship('GroupLoan', back_populates='group')
    savings = db.relationship('GroupSaving', back_populates='group')

    def __repr__(self):
        return f'<Group {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration_number': self.registration_number,
            'location': self.location,
            'description': self.description,
            'meeting_schedule': self.meeting_schedule,
            'status': self.status,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class GroupMembership(Model, TimestampMixin):
    __tablename__ = 'group_memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    role = db.Column(db.String(20))  # chairperson, secretary, treasurer, member
    join_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationships
    user = db.relationship('User', back_populates='groups')
    group = db.relationship('Group', back_populates='members')

    def __repr__(self):
        return f'<GroupMembership {self.user_id} - {self.group_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'role': self.role,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 