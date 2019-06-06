# coding=utf-8

import pdb
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from uqer import DataAPI
import uqer
import sqlalchemy as sa
from sqlalchemy import select, and_

class StockPool(object):
    def __init__(self, **kwargs):
        self._conn = kwargs.get('conn', None)
        self._uqer_token = kwargs.get('uqer_token', None)
        self._is_uqer_init = kwargs.get('is_uqer', 0)
        if self._is_uqer_init == 0 and self._uqer_token is not None:
            uqer.Client(token=self._uqer_token)
            self._is_uqer_init = 1
   
    def fetch_index_uqer(self, trade_date, index):
        index_stock = DataAPI.IdxCloseWeightGet(secID=u"",ticker=str(index.split('.')[0]),
                                         beginDate=trade_date - relativedelta(years=1),
                                         endDate=trade_date,
                                          field=u"effDate,consID,weight",
                                          pandas="1").rename(columns={'consID':'code'}).set_index('effDate')
        trade_date_sets = list(set(index_stock.index))
        trade_date_sets.sort(reverse=False)
        index_stock = index_stock.loc[trade_date_sets[-1]]
        index_stock['trade_date'] = trade_date
        return index_stock
        
    def get_industry_by_day(self, all_stocks, trade_date):
        stock_sets = DataAPI.EquIndustryGet(secID=all_stocks,industryVersionCD=u"010303",
                                      industryID1=u"",
                                      industryID2=u"",
                                      industryID3=u"",
                                      intoDate=trade_date.strftime('%Y%m%d'),
                                      field=u"secID,industryID1",pandas="1")

        stock_sets.rename(columns={'industryID1':'industryID'},inplace=True)
        industry = DataAPI.IndustryGet(
            industryVersion=u"SW",industryVersionCD=u"",
            industryLevel=u"1",isNew=u"1",prntIndustryID=u"",field=u"industryID,industryName,indexSymbol",pandas="1")
        stock_sets = stock_sets.merge(industry, on=['industryID'])[['secID','indexSymbol','industryName']]
        stock_sets = stock_sets.rename(columns={'secID':'code'})
        return stock_sets
    
    def fetch_index(self, trade_date, index):
        if self._is_uqer_init:
            index_df = self.fetch_index_uqer(trade_date, index)
            industry_df = self.get_industry_by_day(list(set(index_df['code'])), trade_date)
            index_df = index_df.merge(industry_df, on=['code'])
            return index_df
    
    def fetch_industry_uqer(self, trade_date, industry = []):
        industry_sets = DataAPI.IndustryGet(
                            industryVersion=u"SW",industryVersionCD=u"",
                            industryLevel=u"1", isNew=u"1", prntIndustryID=u"",
                            field=u"industryID,industryName,indexSymbol",pandas="1")
        if len(industry) > 0:
            industry_sets = industry_sets.set_index('indexSymbol').loc[industry]
        
        equ = DataAPI.EquIndustryGet(industryVersionCD=u"010303",
                                      industryID1=list(set(industry_sets['industryID'])),
                                      intoDate=trade_date.strftime('%Y%m%d'),
                                      field=u"secID,industryID1",pandas="1")
        equ.rename(columns={'industryID1':'industryID'}, inplace=True)
        industry_sets = industry_sets.reset_index().merge(equ, on=['industryID'])[['indexSymbol',
                                                                                   'industryName',
                                                                                   'secID']]
        industry_sets.rename(columns={'secID':'code','indexSymbol':'industryID'},inplace=True)
        industry_sets['trade_date'] = trade_date
        return industry_sets
            
    def fetch_industry(self, trade_date, industry=[]):
        if self._is_uqer_init:
            return self.fetch_industry_uqer(trade_date, industry)

    def on_work_by_interval(self, trade_date_list, main_type, index):
        if self._is_uqer_init:
            stock_pool_list = []
            trade_date_list.sort(reverse=False)
            fact_date_list = trade_date_list[:-1]
            fact_date_list.sort(reverse=False)
            for date in fact_date_list:
                print(date)
                stock_pool_list += self.fetch_index(date, 
                                                index).to_dict(orient='records')
            stock_pool_sets = pd.DataFrame(stock_pool_list)
            if main_type != 1:
                grouped = stock_pool_sets.groupby(by='trade_date')
                stock_pool_list = []
                for k, group in grouped:
                    index = trade_date_list.index(datetime.datetime.strptime(k.strftime('%Y-%m-%d'),'%Y-%m-%d').date())
                    group['trade_date'] = datetime.datetime.strptime(trade_date_list[index+1],'%Y-%m-%d')
                    stock_pool_list += group.to_dict(orient='records')
                stock_pool_sets = pd.DataFrame(stock_pool_list)
            stock_pool_sets['trade_date'] = pd.to_datetime(stock_pool_sets['trade_date'])
            return stock_pool_sets
            