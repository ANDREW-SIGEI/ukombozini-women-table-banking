from app import db
from .base import Model, TimestampMixin, PaginatedAPIMixin, CRUDMixin
from .user import User
from .group import Group, GroupMembership
from .financial import (
    Loan, GroupLoan, Saving, GroupSaving,
    LoanPayment, GroupLoanPayment,
    TableBankingTransaction, TableBankingAccount, TableBankingInterest
)
from .collections import (
    AgricultureCollection, SchoolFeesCollection,
    AgriculturePayment, ServiceFeeCollection, Collection
)
from .accounting import (
    AccountingTransaction, DividendDistribution,
    DividendPayment
)
from .meeting import Meeting, MeetingAttendance
from .products import LoanProduct, SavingProduct
from .field_officer import (
    FieldOfficerAssignment, GroupVisitReport,
    OfficerPerformance, RotationHistory, Visit,
    OfficerRotation, FieldOfficer
)
from .visit_report import VisitReport
from .settings import SystemSetting

# Make all models available at the package level
__all__ = [
    'db',
    'Model',
    'TimestampMixin',
    'PaginatedAPIMixin',
    'CRUDMixin',
    'User',
    'Group',
    'GroupMembership',
    'Loan',
    'GroupLoan',
    'Saving',
    'GroupSaving',
    'LoanPayment',
    'GroupLoanPayment',
    'TableBankingTransaction',
    'TableBankingAccount',
    'TableBankingInterest',
    'AgricultureCollection',
    'SchoolFeesCollection',
    'AgriculturePayment',
    'ServiceFeeCollection',
    'AccountingTransaction',
    'DividendDistribution',
    'DividendPayment',
    'Meeting',
    'MeetingAttendance',
    'LoanProduct',
    'SavingProduct',
    'FieldOfficerAssignment',
    'GroupVisitReport',
    'OfficerPerformance',
    'RotationHistory',
    'SystemSetting',
    'Visit',
    'OfficerRotation',
    'Collection',
    'FieldOfficer',
    'VisitReport'
]
 