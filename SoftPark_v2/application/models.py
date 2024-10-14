from flask_login import UserMixin
from sqlalchemy.sql import func
from decimal import Decimal
from datetime import datetime
from . import db


class Worker(db.Model, UserMixin):
    __tablename__='workers'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_nr = db.Column(db.String(20), nullable=False, unique=True)
    month_fee = db.Column(db.Integer)
    contract_start = db.Column(db.Date, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    barrier_users = db.relationship('BarrierUser')

    def __init__(self, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.month_fee = int(Decimal(self.month_fee) * 100)
        self.contract_start = datetime.strptime(self.contract_start, '%Y-%m-%d')

    ''' Getting a fee value as Decimal (rounded to 2. places). '''
    def get_month_fee(self):
        return round(Decimal(int(self.month_fee) / 100), 2)

    ''' Setting a fee value as Integer. '''
    def set_month_fee(self, amount):
        self.month_fee = int(Decimal(amount) * 100)

    ''' Getting a prettier phone number - using a space as a separator. '''
    def get_phone_nr_with_spaces(self):
        n = 3 # Slice a phone num on every n-th digits.
        sliced_phone_nr = [self.phone_nr[i:i+n] for i in range(0, len(self.phone_nr), n)]
        return ' '.join(sliced_phone_nr)

    ''' Setting a contract start date as a datetime type. '''
    def set_contract_start(self, date):
        self.contract_start = datetime.strptime(date, '%Y-%m-%d')


''' Szlabanownicy ''' 
class BarrierUser(db.Model):
    __tablename__ = 'barrier_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_nr = db.Column(db.String(20), nullable=False, unique=True)
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))


class SmsCode(db.Model):
    __tablename__ = 'sms_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    desc = db.Column(db.String(1000), nullable=False)
