class FieldOfficerGroup(db.Model):
    """Tracks which field officers are assigned to which groups"""
    __tablename__ = 'field_officer_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    rotation_start_date = db.Column(db.DateTime, nullable=False)  # When the rotation starts
    rotation_end_date = db.Column(db.DateTime, nullable=False)    # When the rotation ends
    status = db.Column(db.String(20), default='active')  # active, inactive
    notes = db.Column(db.Text)
    
    # Relationships
    field_officer = db.relationship('User', backref='assigned_groups')
    group = db.relationship('Group', backref='assigned_field_officers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_officer_id': self.field_officer_id,
            'group_id': self.group_id,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'rotation_start_date': self.rotation_start_date.isoformat() if self.rotation_start_date else None,
            'rotation_end_date': self.rotation_end_date.isoformat() if self.rotation_end_date else None,
            'status': self.status,
            'notes': self.notes,
            'field_officer': self.field_officer.to_dict() if self.field_officer else None,
            'group': self.group.to_dict() if self.group else None
        }

class FieldOfficerRotationHistory(db.Model):
    """Tracks historical rotations of field officers"""
    __tablename__ = 'field_officer_rotation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    performance_rating = db.Column(db.Float)  # 1-5 rating
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    field_officer = db.relationship('User', backref='rotation_history')
    group = db.relationship('Group', backref='officer_rotation_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_officer_id': self.field_officer_id,
            'group_id': self.group_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'performance_rating': self.performance_rating,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'field_officer': self.field_officer.to_dict() if self.field_officer else None,
            'group': self.group.to_dict() if self.group else None
        }

class GroupVisitReport(db.Model):
    """Tracks field officer visits to groups"""
    __tablename__ = 'group_visit_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    visit_type = db.Column(db.String(20), nullable=False)  # regular, special, emergency
    attendance_count = db.Column(db.Integer)
    meeting_summary = db.Column(db.Text)
    issues_identified = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    field_officer = db.relationship('User', backref='visit_reports')
    group = db.relationship('Group', backref='visit_reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_officer_id': self.field_officer_id,
            'group_id': self.group_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'visit_type': self.visit_type,
            'attendance_count': self.attendance_count,
            'meeting_summary': self.meeting_summary,
            'issues_identified': self.issues_identified,
            'recommendations': self.recommendations,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'field_officer': self.field_officer.to_dict() if self.field_officer else None,
            'group': self.group.to_dict() if self.group else None
        }

class FieldOfficerPerformance(db.Model):
    """Tracks field officer performance metrics"""
    __tablename__ = 'field_officer_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    groups_visited = db.Column(db.Integer, default=0)
    meetings_attended = db.Column(db.Integer, default=0)
    issues_resolved = db.Column(db.Integer, default=0)
    average_attendance = db.Column(db.Float)
    performance_score = db.Column(db.Float)  # 0-100
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    field_officer = db.relationship('User', backref='performance_metrics')
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_officer_id': self.field_officer_id,
            'month': self.month,
            'year': self.year,
            'groups_visited': self.groups_visited,
            'meetings_attended': self.meetings_attended,
            'issues_resolved': self.issues_resolved,
            'average_attendance': self.average_attendance,
            'performance_score': self.performance_score,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'field_officer': self.field_officer.to_dict() if self.field_officer else None
        }

class FieldOfficerReport(db.Model):
    __tablename__ = 'field_officer_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    field_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Group attendance details
    groups_attended = db.relationship('GroupAttendance', backref='report', lazy=True)
    
    # Financial details
    service_fees = db.relationship('ServiceFee', backref='report', lazy=True)
    project_registration_fees = db.relationship('ProjectRegistrationFee', backref='report', lazy=True)
    new_member_fees = db.relationship('NewMemberFee', backref='report', lazy=True)
    loan_collections = db.relationship('LoanCollection', backref='report', lazy=True)
    project_collections = db.relationship('ProjectCollection', backref='report', lazy=True)
    welfare_collections = db.relationship('WelfareCollection', backref='report', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_officer_id': self.field_officer_id,
            'report_date': self.report_date.isoformat(),
            'groups_attended': [g.to_dict() for g in self.groups_attended],
            'service_fees': [f.to_dict() for f in self.service_fees],
            'project_registration_fees': [f.to_dict() for f in self.project_registration_fees],
            'new_member_fees': [f.to_dict() for f in self.new_member_fees],
            'loan_collections': [c.to_dict() for c in self.loan_collections],
            'project_collections': [c.to_dict() for c in self.project_collections],
            'welfare_collections': [c.to_dict() for c in self.welfare_collections],
            'total_collections': self.calculate_total_collections()
        }
    
    def calculate_total_collections(self):
        total = 0
        total += sum(f.amount for f in self.service_fees)
        total += sum(f.amount for f in self.project_registration_fees)
        total += sum(f.amount for f in self.new_member_fees)
        total += sum(c.amount for c in self.loan_collections)
        total += sum(c.amount for c in self.project_collections)
        total += sum(c.amount for c in self.welfare_collections)
        return total

class GroupAttendance(db.Model):
    __tablename__ = 'group_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    attendance_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'attendance_time': self.attendance_time.isoformat(),
            'notes': self.notes
        }

class ServiceFee(db.Model):
    __tablename__ = 'service_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'amount': float(self.amount),
            'notes': self.notes
        }

class ProjectRegistrationFee(db.Model):
    __tablename__ = 'project_registration_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    project_name = db.Column(db.String(128), nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'amount': float(self.amount),
            'project_name': self.project_name,
            'notes': self.notes
        }

class NewMemberFee(db.Model):
    __tablename__ = 'new_member_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'member_id': self.member_id,
            'amount': float(self.amount),
            'notes': self.notes
        }

class LoanCollection(db.Model):
    __tablename__ = 'loan_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'loan_id': self.loan_id,
            'amount': float(self.amount),
            'notes': self.notes
        }

class ProjectCollection(db.Model):
    __tablename__ = 'project_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    project_name = db.Column(db.String(128), nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'amount': float(self.amount),
            'project_name': self.project_name,
            'notes': self.notes
        }

class WelfareCollection(db.Model):
    __tablename__ = 'welfare_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('field_officer_reports.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(db.String(128))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'amount': float(self.amount),
            'purpose': self.purpose,
            'notes': self.notes
        } 