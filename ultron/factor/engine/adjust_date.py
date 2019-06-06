# coding=utf-8

import datetime
from PyFin.api import DateUtilities

class AdjustTradeDate(object):
    def __init__(self, **kwargs):
        self._conn = kwargs.get('conn', None)
        self._uqer_token = kwargs.get('uqer_token', None)
        is_uqer_init = kwargs.get('is_uqer', 0)
        if is_uqer_init == 0:
            #uqer初始化时连接互联网，故放此处引用
            import uqer
            uqer.Client(token=self._uqer_token)
     
    def _fetch_all_date(self, start_date, end_date, columns):
        from uqer import DataAPI
        field = 'calendarDate,' + columns
        df = DataAPI.TradeCalGet(exchangeCD=u"XSHG",beginDate=start_date,
                                 endDate=end_date, field=field,pandas="1")
        return df
        
    def custom_fetch_end(self, start_date, end_date, columns):
        df = self._fetch_all_date(start_date, end_date, columns)
        df = df[df[columns] == 1]
        str_trade_date_list = list(set(df['calendarDate']))
        trade_date_list = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in str_trade_date_list]
        return trade_date_list
    
    def custom_fetch_date(self, start_date, end_date, interval):
        from uqer import DataAPI
        df = DataAPI.TradeCalGet(exchangeCD=u"XSHG",beginDate=start_date,
                                 endDate=end_date, field='calendarDate,isOpen',pandas="1")
        df = df[df['isOpen']==1]
        str_trade_date_list = list(set(df['calendarDate']))
        str_trade_date_list.sort(reverse=False)
        str_trade_date_list = list(filter(lambda x: str_trade_date_list.index(x) % interval == 0, str_trade_date_list))
        trade_date_list = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in str_trade_date_list]
        return trade_date_list
    