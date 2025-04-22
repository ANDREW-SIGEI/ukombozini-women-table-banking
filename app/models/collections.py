from datetime import datetime
from app import db
from app.models.base import Model, TimestampMixin, PaginatedAPIMixin

class Collection(Model, TimestampMixin):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)
    collection_type = db.Column(db.String(20), nullable=False)  # loan_repayment, savings, fee
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref=db.backref('collections', lazy=True))
    member = db.relationship('User', backref=db.backref('collections', lazy=True))
    
    def __repr__(self):
        return f'<Collection {self.id}: {self.collection_type} from {self.member_id}>'

class AgricultureCollection(db.Model):
    __tablename__ = 'agriculture_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    product_name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, ton, bag, etc
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    collection_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # collected, sold, distributed
    storage_location = db.Column(db.String(128))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('agriculture_collections', lazy=True))
    group = db.relationship('Group', backref=db.backref('agriculture_collections', lazy=True))
    
    def __repr__(self):
        return f'<AgricultureCollection {self.id}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'product_name': self.product_name,
            'quantity': float(self.quantity),
            'unit': self.unit,
            'unit_price': float(self.unit_price),
            'total_amount': float(self.total_amount),
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'status': self.status,
            'storage_location': self.storage_location,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page=page, per_page=per_page, error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            }
        }
        return data

class SchoolFeesCollection(db.Model):
    __tablename__ = 'school_fees_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    student_name = db.Column(db.String(128), nullable=False)
    school_name = db.Column(db.String(128), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    payment_method = db.Column(db.String(20))
    reference_number = db.Column(db.String(64))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('school_fees_collections', lazy=True))
    group = db.relationship('Group', backref=db.backref('school_fees_collections', lazy=True))
    
    def __repr__(self):
        return f'<SchoolFeesCollection {self.id}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'student_name': self.student_name,
            'school_name': self.school_name,
            'term': self.term,
            'year': self.year,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page=page, per_page=per_page, error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            }
        }
        return data

class AgriculturePayment(db.Model):
    __tablename__ = 'agriculture_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('agriculture_collections.id'), index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(20))
    reference_number = db.Column(db.String(64))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    
    # Relationships
    collection = db.relationship('AgricultureCollection', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return f'<AgriculturePayment {self.id}>'

class ServiceFeeCollection(Model, TimestampMixin):
    """Model for service fee collections by field officers"""
    __tablename__ = 'service_fee_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    collection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref='service_fees')
    officer = db.relationship('User', backref='service_fees_collected')
    
    def __repr__(self):
        return f'<ServiceFeeCollection {self.id}: {self.amount} KES>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'officer_id': self.officer_id,
            'amount': self.amount,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RegistrationFeeCollection(Model, TimestampMixin):
    """Model for registration fee collections"""
    __tablename__ = 'registration_fee_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_amount = db.Column(db.Integer, nullable=False, default=0)
    member_amount = db.Column(db.Integer, nullable=False, default=0)
    collection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref='registration_fees')
    officer = db.relationship('User', backref='registration_fees_collected')
    
    def __repr__(self):
        return f'<RegistrationFeeCollection {self.id}: P:{self.project_amount} M:{self.member_amount} KES>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'officer_id': self.officer_id,
            'project_amount': self.project_amount,
            'member_amount': self.member_amount,
            'total_amount': self.project_amount + self.member_amount,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LoanCollection(Model, TimestampMixin):
    """Model for loan collections"""
    __tablename__ = 'loan_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False, default='cash')
    collection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref='loan_collections')
    officer = db.relationship('User', backref='loan_collections_processed')
    
    def __repr__(self):
        return f'<LoanCollection {self.id}: {self.amount} KES>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'officer_id': self.officer_id,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectFundCollection(Model, TimestampMixin):
    """Model for project fund collections"""
    __tablename__ = 'project_fund_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    project_type = db.Column(db.String(50), nullable=False, default='other')
    collection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref='project_fund_collections')
    officer = db.relationship('User', backref='project_funds_collected')
    
    def __repr__(self):
        return f'<ProjectFundCollection {self.id}: {self.amount} KES>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'officer_id': self.officer_id,
            'amount': self.amount,
            'project_type': self.project_type,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WelfareCollection(Model, TimestampMixin):
    """Model for welfare collections"""
    __tablename__ = 'welfare_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(50), nullable=False, default='general')
    collection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    group = db.relationship('Group', backref='welfare_collections')
    officer = db.relationship('User', backref='welfare_collections_processed')
    
    def __repr__(self):
        return f'<WelfareCollection {self.id}: {self.amount} KES>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'officer_id': self.officer_id,
            'amount': self.amount,
            'purpose': self.purpose,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AgricultureMonthlyCollection(Model, TimestampMixin):
    """Model for agriculture monthly collections from January to August with interest calculation"""
    __tablename__ = 'agriculture_monthly_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True, nullable=True)
    year = db.Column(db.Integer, nullable=False)
    january = db.Column(db.Integer, default=0)
    february = db.Column(db.Integer, default=0)
    march = db.Column(db.Integer, default=0)
    april = db.Column(db.Integer, default=0)
    may = db.Column(db.Integer, default=0)
    june = db.Column(db.Integer, default=0)
    july = db.Column(db.Integer, default=0)
    august = db.Column(db.Integer, default=0)
    total_saved = db.Column(db.Integer, default=0)
    interest_amount = db.Column(db.Integer, default=0)  # Half of the total saved
    total_payable = db.Column(db.Integer, default=0)  # Total saved + interest
    status = db.Column(db.String(20), default='active')  # active, paid, cancelled
    paying_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('agriculture_monthly_collections', lazy=True))
    group = db.relationship('Group', backref=db.backref('agriculture_monthly_collections', lazy=True))
    paying_officer = db.relationship('User', foreign_keys=[paying_officer_id], backref=db.backref('agriculture_monthly_payments', lazy=True))
    
    def __repr__(self):
        return f'<AgricultureMonthlyCollection {self.id}: {self.user_id} - {self.year}>'
    
    def calculate_totals(self):
        """Calculate total saved, interest and total payable"""
        self.total_saved = sum([
            self.january or 0,
            self.february or 0,
            self.march or 0,
            self.april or 0,
            self.may or 0,
            self.june or 0,
            self.july or 0,
            self.august or 0
        ])
        self.interest_amount = self.total_saved // 2  # Half of the total saved
        self.total_payable = self.total_saved + self.interest_amount
        return self
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'year': self.year,
            'january': self.january,
            'february': self.february,
            'march': self.march,
            'april': self.april,
            'may': self.may,
            'june': self.june,
            'july': self.july,
            'august': self.august,
            'total_saved': self.total_saved,
            'interest_amount': self.interest_amount,
            'total_payable': self.total_payable,
            'status': self.status,
            'paying_officer_id': self.paying_officer_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 