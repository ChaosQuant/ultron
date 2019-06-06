# coding=utf-8

import sys
sys.path.append('..')
import datetime
from ultron.factor.engine.adjust_date import AdjustTradeDate
from ultron.factor.engine.stock_pool import StockPool
import pdb

pdb.set_trace()
adjust_date = AdjustTradeDate(uqer_token='',
                              is_uqer=0)
trade_date_list = adjust_date.custom_fetch_end(datetime.datetime(2018,1,1), datetime.datetime(2018,12,31),'isWeekEnd')

stock_pool = StockPool(uqer_token='',
                       is_uqer=1)
index = '000905.XSHG'

stock_sets = stock_pool.on_work_by_interval(trade_date_list, 1, index)