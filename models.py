from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ssn = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    accounts = relationship("Account", back_populates="customer")

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, default=0, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="accounts")

class Banks(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, default=0, nullable=False)
    bank_nr = Column(String, unique=True, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)
    amount = Column(Numeric, default=0, nullable=False)
    timestamp = Column(DateTime, default=DateTime)
    currency = Column(String, nullable=False)
    sender_account = Column(String, nullable=False)
    receiver_account = Column(String, nullable=False)
    sender_country = Column(String, nullable=False)
    sender_municipality = Column(String, nullable=False)
    receiver_country = Column(String, nullable=False)
    receiver_municipality = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    notes = Column(String, nullable=False)


