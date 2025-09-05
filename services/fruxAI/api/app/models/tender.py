from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Text, DECIMAL, TIMESTAMP, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(2), nullable=False, index=True)
    file_name = Column(String(255), nullable=False, index=True)
    contract_number = Column(String(50), index=True)
    project_id = Column(String(50), index=True)
    bid_opening_date = Column(Date)
    title = Column(Text)
    location = Column(Text)
    winner_firm_id = Column(String(100))
    winner_amount = Column(DECIMAL(15, 2))
    currency = Column(String(3), default='USD')
    extraction_info = Column(JSON)
    status = Column(String(20), default='active')
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(2), nullable=False, index=True)
    tender_id = Column(Integer, index=True)
    firm_id = Column(String(100), nullable=False)
    bid_amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    rank = Column(Integer)
    preference = Column(String(10))
    cslb_number = Column(String(50))
    name_official = Column(Text)

class Firm(Base):
    __tablename__ = "firms"

    state = Column(String(2), nullable=False, primary_key=True)
    firm_id = Column(String(100), nullable=False, primary_key=True)
    name_official = Column(Text)
    cslb_number = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    state_code = Column(String(2))
    zip = Column(String(10))
    phone = Column(String(20))
    fax = Column(String(20))
    created_at = Column(TIMESTAMP, default=func.now())

class TenderWinnerHistory(Base):
    __tablename__ = "tender_winner_history"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(2), nullable=False, index=True)
    tender_id = Column(Integer, index=True)
    firm_id = Column(String(100))
    source = Column(String(20))  # 'auto_detect', 'manual_override'
    changed_by = Column(String(100))
    changed_at = Column(TIMESTAMP, default=func.now())
    note = Column(Text)

