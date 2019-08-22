# coding=utf-8
import datetime
import pandas as pd
import numpy as np
from sqlalchemy import select, and_
import sqlalchemy as sa
from ultron.optimization.calc_pool import CalcPool

class RawFactors(object):
    def __init__(self, db_info):
        self._factors_info = db_info
        self._calc_pool = CalcPool()
    
    def callback_factors(self, conn, params):
        trade_date = params[0]
        table = params[1]
        code_name = params[2]
        trade_name = params[3]
        columns = params[4]
        
        db_columns = []
        if len(columns) == 0:
            db_columns.append(table)
        else:
            db_columns.append(table.__dict__[code_name])
            db_columns.append(table.__dict__[trade_name])
            for column in columns:
                db_columns.append(table.__dict__[column])
        query = select(db_columns).where(
            and_(
                table.trade_date == trade_date
            )
        ).order_by(table.trade_date)
        df = pd.read_sql(query, con=sa.create_engine(self._factors_info))
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df
        
        
    def custom_factors_by_interval(self, trade_date_list, table, code_name, trade_name, columns):
        db_columns = []
        if len(columns) == 0:
            db_columns.append(table)
        else:
            db_columns.append(table.__dict__[code_name])
            db_columns.append(table.__dict__[trade_name])
            for column in columns:
                db_columns.append(table.__dict__[column])
        query = select(db_columns).where(
            and_(
                table.trade_date.in_(trade_date_list)
            )
        ).order_by(table.trade_date)
        df = pd.read_sql(query, con=sa.create_engine(self._factors_info))
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df
        
    def on_work_by_interval(self, trade_date_list, table, code_name, trade_name, columns=[], is_pool=False):
        trade_date_list.sort(reverse=False)
        if not is_pool: 
            factor_sets = self.custom_factors_by_interval(trade_date_list[:-1], table, code_name,
                                                          trade_name, columns)
        else:
            params_list = []
            for trade_date in trade_date_list:
                params_list.append([trade_date, table, code_name, trade_name, columns])
            factor_sets = self._calc_pool.calc_work_db(self._factors_info, self.callback_factors, params_list)
        return factor_sets