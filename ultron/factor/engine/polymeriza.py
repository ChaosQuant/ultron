# coding=utf-8

import json
import datetime
import importlib
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import select, and_
from ultron.factor.engine.raw_factors import RawFactors

class Polymerization(object):
    def __init__(self, common_setting = None,
                 file_setting = None):
        self._file_setting = file_setting
        self._common_setting = common_setting
        self._risk_info = {}
        self._market_info = {}
        self._load_setting()
   
    def _load_setting(self):
        # 通用数据
        if self._file_setting is not None:
            with open(self._common_setting) as f:
                common_info = json.load(f)
                self._market_info['conn'] = sa.create_engine(common_info['market']['conn'])
                self._risk_info['conn'] = sa.create_engine(common_info['risk']['conn'])
                self._market_info['table'] = importlib.import_module(common_info['market']['model']).__getattribute__(
                                         common_info['market']['table'])
                self._risk_info['table'] = importlib.import_module(common_info['risk']['model']).__getattribute__(
                                         common_info['risk']['table'])
                self._risk_info['trade_date'] = self._risk_info['table'].__dict__[common_info['risk']['trade_date']]
            
                self._market_info['trade_date'] = self._market_info['table'].__dict__[common_info['market']['trade_date']]
                self._market_info['tclose'] = self._market_info['table'].__dict__[common_info['market']['tclose']]
                self._market_info['code'] = self._market_info['table'].__dict__[common_info['market']['code']]
                self._market_info['columns'] = common_info['market']['columns']
        #因子数据
        if self._common_setting is not None:
            with open(self._file_setting) as f:
                self._factors_setting = json.load(f)
    
    def on_return_by_interval(self, trade_date_list):
        db_columns = []
        table = self._market_info['table']
        db_columns.append(self._market_info['trade_date'])
        db_columns.append(self._market_info['tclose'])
        db_columns.append(self._market_info['code'])
        columns = self._market_info['columns']
        for column in columns:
            db_columns.append(table.__dict__[column])
        query = select(db_columns).where(
            and_(
                self._market_info['trade_date'].in_(trade_date_list)
            )
        ).order_by(self._market_info['trade_date'])
                
        df = pd.read_sql(query, con=self._market_info['conn'])
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.sort_values(by='trade_date')
        return df
    
    def on_risk_by_interval(self, trade_date_list):
        db_columns = []
        db_columns.append(self._risk_info['table'])
        query = select(db_columns).where(
            and_(
                self._risk_info['trade_date'].in_(trade_date_list)
            )
        ).order_by(self._risk_info['trade_date'])
        df = pd.read_sql(query, con=self._risk_info['conn'])
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.sort_values(by='trade_date')
        return df
    
    def on_work_by_factors(self, trade_date_list, factors_setting):
        factors_sets = None
        for setting in factors_setting:
            conn = setting['conn']
            factors_list = setting['factors']
            for factor in factors_list:
                raw_factors = RawFactors(conn)
                model_name = factor['model']
                table_name = factor['table']
                code_name = factor['code']
                trade_date_name = factor['trade_date']
                columns =  factor['columns']
                module = importlib.import_module(model_name)
                table = module.__getattribute__(table_name)
                factor_sets = raw_factors.on_work_by_interval(trade_date_list, table, code_name, trade_date_name,
                                                              columns)
                if code_name != 'code':
                    factor_sets = factor_sets.rename(columns={'symbol':'code'})
                if factors_sets is None:
                    factors_sets = factor_sets
                else:
                    factors_sets = factors_sets.merge(factor_sets, on=['code','trade_date'])
        return factors_sets
    
    def on_main_factors(self, trade_date_list, factor_sets, return_sets):
        #以因子日期为主，即把T+1的收益放在T期
        trade_date_list.sort(reverse=False)
        grouped = return_sets.groupby(by='trade_date')
        new_return_list = []
        for k, group in grouped:
            index = trade_date_list.index(datetime.datetime.strptime(k.strftime('%Y-%m-%d'),'%Y-%m-%d').date())
            group.loc[:,'trade_date'] = trade_date_list[index-1]
            new_return_list += group.to_dict(orient='records')
        new_return_sets = pd.DataFrame(new_return_list)
        new_return_sets['trade_date'] = pd.to_datetime(new_return_sets['trade_date'])
        return factor_sets.merge(new_return_sets, on=['code', 'trade_date'])
        
    def on_main_return(self, trade_date_list, factors, return_sets):
        #以收益率日期为主,即把T期因子放在T+1期
        trade_date_list.sort(reverse=False)
        grouped = factors.groupby(by='trade_date')
        factors_list = []
        for k, group in grouped:
            index = trade_date_list.index(datetime.datetime.strptime(k.strftime('%Y-%m-%d'),'%Y-%m-%d').date())
            group['trade_date'] = trade_date_list[index-1]
            factors_list += group.to_dict(orient='records')
        new_factors_sets = pd.DataFrame(factors_list)
        return new_factors_sets.merge(return_sets, on=['code', 'trade_date'])
    
    def custom_work_by_interval(self, trade_date_list, main_type, factor_info):
        factors_setting = json.loads(factor_info)
        return self.on_work_by_factors(trade_date_list[:-1], factors_setting)
        
    def on_work_by_interval(self, trade_date_list, main_type=1, is_rename = 1):
        trade_date_list.sort(reverse=False)
        factors_sets = self.on_work_by_factors(trade_date_list[:-1], self._factors_setting)
        #获取当期收益率
        now_return_sets = self.on_return_by_interval(trade_date_list[:-1])
        factors_sets = factors_sets.merge(now_return_sets,on=['code','trade_date']).rename(columns={self._market_info['tclose'].name:'oclosePrice'})
        return_sets = self.on_return_by_interval(trade_date_list[1:])
        return_sets = return_sets.rename(columns={self._market_info['tclose'].name:'nclosePrice'})
        if main_type == 1: # 当前日期为T
            factors_sets = self.on_main_factors(trade_date_list, factors_sets, return_sets)
        else: # 当前日期为T+1
            factors_sets = self.on_main_return(trade_date_list, factors_sets, return_sets)
        factors_sets['chgPct']  = (factors_sets['nclosePrice'] / factors_sets['oclosePrice']) -1
        #加入风险因子
        risk_sets = self.on_risk_by_interval(trade_date_list)
        if is_rename:
            risk_sets.rename(columns={'Bank':'801780','RealEstate':'801180','Health':'801150',
                                 'Transportation':'801170','Mining':'801020','NonFerMetal':'801050',
                                 'HouseApp':'801110','LeiService':'801210','MachiEquip':'801890',
                                 'BuildDeco':'801720','CommeTrade':'801200','CONMAT':'801710',
                                 'Auto':'801880','Textile':'801130','FoodBever':'801120',
                                 'Electronics':'801080','Computer':'801750','LightIndus':'801140',
                                 'Utilities':'801160','Telecom':'801770','AgriForest':'801010',
                                 'CHEM':'801030','Media':'801760','IronSteel':'801040','NonBankFinan':'801790',
                                 'ELECEQP':'801730','AERODEF':'801740','Conglomerates':'801230'}, inplace=True)
        factors_sets = factors_sets.merge(risk_sets, on=['code','trade_date'])
        return factors_sets