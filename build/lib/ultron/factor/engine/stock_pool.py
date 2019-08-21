# coding=utf-8

import pdb
import pandas as pd
import json
import importlib
import sqlalchemy as sa
from sqlalchemy import select, and_

class StockPool(object):
    def __init__(self, file_setting):
        self._file_setting = file_setting
        self._index_info = {}
        self._industry_info = {}
        self._load_setting()

    def _load_setting(self):
        with open(self._file_setting) as f:
            file_info = json.load(f)
            self._index_info['conn'] = sa.create_engine(file_info['index']['conn'])
            self._index_info['table'] = importlib.import_module(file_info['index']['model']).__getattribute__(
                                         file_info['index']['table'])
            self._index_info['trade_date'] = self._index_info['table'].__dict__[file_info['index']['trade_date']]
            self._index_info['code'] = self._index_info['table'].__dict__[file_info['index']['code']]
            self._index_info['flag'] = self._index_info['table'].__dict__[file_info['index']['flag']]
            self._index_info['columns'] = file_info['index']['columns']
            
            self._industry_info['conn'] = sa.create_engine(file_info['industry']['conn'])
            self._industry_info['table'] = importlib.import_module(file_info['industry']['model']).__getattribute__(
                                         file_info['industry']['table'])
            self._industry_info['trade_date'] = self._industry_info['table'].__dict__[file_info['industry']['trade_date']]
            self._industry_info['code'] = self._industry_info['table'].__dict__[file_info['industry']['code']]
            self._industry_info['flag'] = self._industry_info['table'].__dict__[file_info['industry']['flag']]
            self._industry_info['columns'] = file_info['industry']['columns']
            
    def on_index_by_interval(self, trade_date_list, index):
        db_columns = []
        table = self._index_info['table']
        db_columns.append(self._index_info['trade_date'])
        db_columns.append(self._index_info['code'])
        db_columns.append(self._index_info['flag'])
        columns = self._index_info['columns']
        for column in columns:
            db_columns.append(table.__dict__[column])
        query = select(db_columns).where(
            and_(
                self._index_info['trade_date'].in_(trade_date_list),
                self._index_info['flag'] == index
            )
        )
                
        df = pd.read_sql(query, con=self._index_info['conn'])
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.sort_values(by='trade_date')
        return df
    
    def on_industry_by_interval(self, trade_date_list, industry_id):
        db_columns = []
        table = self._industry_info['table']
        db_columns.append(self._industry_info['trade_date'])
        db_columns.append(self._industry_info['code'])
        db_columns.append(self._industry_info['flag'])
        columns = self._industry_info['columns']
        for column in columns:
            db_columns.append(table.__dict__[column])
        query = select(db_columns).where(
            and_(
                self._industry_info['trade_date'].in_(trade_date_list),
                self._industry_info['flag'] == industry_id
            )
        )
                
        df = pd.read_sql(query, con=self._industry_info['conn'])
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.sort_values(by='trade_date')
        return df
    
        
    def on_work_by_interval(self, trade_date_list, index, industry_id):
        trade_date_list.sort(reverse=False)
        index_df = self.on_index_by_interval(trade_date_list, index)
        industry_df = self.on_industry_by_interval(trade_date_list, industry_id)
        return index_df.merge(industry_df, on=['code','trade_date'])