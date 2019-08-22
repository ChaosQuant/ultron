# coding=utf-8

import pdb
import sys
sys.path.append('..')
from sqlalchemy import Integer, String, Float, Column, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy import select, and_, func

import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

from PyFin.api import DateUtilities
from ultron.optimization.calc_pool import CalcPool

import numba as nb

Base = declarative_base()
metadata = Base.metadata

class Market5MinBar(Base):
    __tablename__ = 'market_bar_5mins'
    trade_date = Column(TIMESTAMP, primary_key=True, nullable=False)
    code = Column(Integer, primary_key=True, nullable=False)
    bar_time = Column(String)
    close_price = Column(Float(53))
    high_price = Column(Float(53))
    low_price = Column(Float(53))
    open_price = Column(Float(53))
    total_value = Column(Float(53))
    total_volume = Column(Float(53))
    vwap = Column(Float(53))
    twap = Column(Float(53))
    accumadjfactor = Column(Float(53))
 

##多进程调用数据库回调函数
def calc_factor_by_db(conn: object, trade_date: datetime.datetime) -> pd.DataFrame:
    table = Market5MinBar
    query = select([table.trade_date,table.code,table.bar_time,table.close_price,
                    table.total_volume]).where(and_(Market5MinBar.trade_date == trade_date))
    res = pd.read_sql(query,conn)
    return res

##多进程计算函数

###pandas 列子
'''
def calc_factor_by_mean(param: object) -> pd.DataFrame:
    k = param[0]
    g = param[1]
    n_windows = param[2]
    g = g.sort_values(by='trade_date', ascending=True)
    g[str(n_windows) + '_volume'] = g['total_volume'].rolling(window=n_windows).mean()#.shift(1)
    return g[['trade_date',str(n_windows) + '_volume','code']].dropna()
'''


## numpy + numba 例子
## 仅仅为了实现而实现，pandas内置函数效率高于 numba
@nb.njit(nogil=True, cache=True)
def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

@nb.jit
def calc_mean(g, n_windows):
    b = np.mean(rolling_window(g, n_windows), -1)
    return b

def calc_factor_by_mean(param: object):
    k = param[0]
    g = param[1]
    n_windows = param[2]
    return calc_mean(g, n_windows)

    
    
if __name__ == '__main__':
    calc_pool = CalcPool()
    begin_date = datetime.datetime(2018,1,4).date()
    db_info = 'postgresql+psycopg2://alpha:alpha@180.166.26.82:8889/alpha'
    temp_trade_date_list = DateUtilities.makeSchedule(begin_date-relativedelta(days=int(2 * 5)), 
                                                      begin_date,'1b','china.sse')
    temp_trade_date_list.sort(reverse=False)

    res = calc_pool.calc_work_db(db_info, calc_factor_by_db, temp_trade_date_list)
    params_list = []
    grouped = res.groupby(['trade_date','code'])
    for k, g in grouped:
        params_list.append([k,g.total_volume.values,5])
        
    mean_res = calc_pool.calc_work_method(calc_factor_by_mean, params_list, is_pandas = False)
    print(mean_res)
