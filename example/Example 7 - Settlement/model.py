# -*- coding: utf-8 -*-
from sqlalchemy import BigInteger, Column, DateTime, Float, Index, Integer, String, Text, Boolean, text, JSON,TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Experimental(Base):
    __tablename__ = 'experimental'
    trade_date = Column(DateTime, primary_key=True, nullable=False)
    code = Column(Integer, primary_key=True, nullable=False)
    ROEAfterNonRecurring = Column(Float(53))
    EPAfterNonRecurring = Column(Float(53))
    CHV = Column(Float(53))
    DROE = Column(Float(53))
    IVR = Column(Float(53))
    EPAfterNonRecurring = Column(Float(53))
    DROEAfterNonRecurring = Column(Float(53))
    CFinc1 = Column(Float(53))
    ivr_day = Column(Float(53))
    roe_q = Column(Float(53))
    idl_mtm_20 = Column(Float(53))