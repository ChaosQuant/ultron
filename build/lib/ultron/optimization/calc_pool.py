# coding=utf-8
import multiprocessing
import pandas as pd
import datetime
import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy import select, and_, func

class CalcPool(object):
    
    def __init__(self, is_debug=False):
        __str__ = 'calc_pool'
        self._cpus = multiprocessing.cpu_count()
        self._is_debug = is_debug
        
    def _calc_fetch_info(self, cond):
        conn = sa.create_engine(cond[0], poolclass=NullPool)
        callback = cond[1]
        cond = cond[2]
        return callback(conn, cond)
    
    def calc_work_db(self, db_info, callback, params_list):
        cond_list = []
        for param in params_list:
            cond_list.append([db_info, callback, param])
            
        with multiprocessing.Pool(processes=self._cpus) as p:
            res = p.map(self._calc_fetch_info, cond_list)

        return pd.concat(res).reset_index(drop=True)
    
    def calc_work_method(self, callback, params_list, is_pandas=True):
        with multiprocessing.Pool(processes=self._cpus) as p:
            res = p.map(callback, params_list)
        return pd.concat(res).reset_index(drop=True) if is_pandas else res