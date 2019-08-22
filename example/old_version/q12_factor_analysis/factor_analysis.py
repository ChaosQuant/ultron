# coding = utf-8

import pdb
import pandas as pd
import numpy as np
import time
import datetime
import json
import multiprocessing
import statsmodels.api as sm
from scipy.stats import ttest_1samp

from alphamind.api import *
from PyFin.api import *
from PyFin.api import makeSchedule
from alphamind.api import *
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
from alphamind.data.quantile import quantile
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.pool import NullPool
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from models import Alpha191

import sys
sys.path.append('../..')
from ultron.cluster.invoke.app_engine import create_app

app = create_app('factor_analysis')

def update_destdb(destsession, table_name, sets):
    sets = sets.where(pd.notnull(sets), None)
    sql_pe = 'INSERT INTO {0} SET'.format(table_name)
    updates = ",".join( "{0} = :{0}".format(x) for x in list(sets) )
    sql_pe = sql_pe + '\n' + updates
    sql_pe = sql_pe + '\n' +  'ON DUPLICATE KEY UPDATE'
    sql_pe = sql_pe + '\n' + updates
    session = destsession()
    print('update_destdb')
    for index, row in sets.iterrows():
        dict_input = dict( row )
        #dict_input['trade_date'] = dict_input['trade_date'].to_pydatetime()
        session.execute(sql_pe, dict_input)
    session.commit()
    session.close()
    

def prc_win_std(params):
    df = params[0]
    factor_name = params[1]
    ret_preprocess = factor_processing(df[[factor_name]].values,
                                       pre_process=[winsorize_normal, standardize],
                                  )
    df["prc_factor"] = ret_preprocess
    return df

def factor_shift(params):
    g = params[0]
    ms = params[1]
    for i in range(1, ms+1):
        g["prc_factor_l"+str(i)] = g["prc_factor"].shift(i)
    return g


def fetch_factor(engine191, factor_name, start_date, end_date):
    query = select([Alpha191.trade_date, Alpha191.code, Alpha191.__dict__[factor_name]]).where(
        and_(Alpha191.trade_date >= start_date, Alpha191.trade_date <= end_date, ))
    return pd.read_sql(query, engine191)

def factor_combination(engine, factors, universe_name, start_date, end_date, freq):
    universe = Universe(universe_name)
    dates = makeSchedule(start_date, end_date, freq, calendar='china.sse')
    factor_negMkt = engine.fetch_factor_range(universe, "negMarketValue", dates=dates)
    risk_cov, risk_factors = engine.fetch_risk_model_range(universe, dates=dates)
    dx_returns = engine.fetch_dx_return_range(universe, dates=dates, horizon=map_freq(freq))

    # data combination
    total_data = pd.merge(factors, risk_factors, on=['trade_date', 'code'])
    total_data = pd.merge(total_data, factor_negMkt, on=['trade_date', 'code'])
    total_data = pd.merge(total_data, dx_returns, on=['trade_date', 'code'])
    
    industry_category = engine.fetch_industry_range(universe, dates=dates)
    total_data = pd.merge(total_data, industry_category, on=['trade_date', 'code']).dropna()
    total_data.dropna(inplace=True)
    return total_data

def factor_process(total_data,factor_name, neutralized_styles):
    grouped_list = []
    grouped = total_data.groupby(['trade_date'])
    for k, g in grouped:
        grouped_list.append([g,factor_name])
    
    '''
    cpus = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=cpus) as p:
        alpha_res = p.map(prc_win_std, grouped_list)
    '''
    alpha_res = []
    for params in grouped_list:
        alpha_res.append(prc_win_std(params))
        
        
    total_data = pd.concat(alpha_res).reset_index(drop=True)
    prc_factor = neutralize(total_data[neutralized_styles].values.astype(float),
                        total_data["prc_factor"].values,
                                 groups=total_data['trade_date'])
    total_data["prc_factor"] = prc_factor
    return total_data

# 五分位收益计算
def cum_quintile(total_data):
    n_bins=5
    df = pd.DataFrame(columns=['q' + str(i) for i in range(1, n_bins+1)])
    grouped = total_data.groupby('trade_date')
    for k, g in grouped:
        er = g['prc_factor'].values
        dx_return = g['dx'].values
        res = er_quantile_analysis(er, n_bins=n_bins, dx_return=dx_return, de_trend=True)
        df.loc[k, :] = res
    df.index.name = 'trade_date'
    df = df.reset_index()
    return df

# 五分位收益和超额收益
def excess_quintile(destsession, session, factor_name, task_id, df):
    cum_df = df
    cum_df['session'] = session
    cum_df['factor_name'] = factor_name
    cum_df['task_id'] =  task_id
    cum_df['q0'] = cum_df.q5 - cum_df.q1
    cum_df[['q0','q1','q2','q3','q4','q5']] = cum_df[['q0','q1','q2','q3','q4','q5']].cumsum()
    cum_df['trade_date'] = cum_df['trade_date'].apply(lambda x : x.to_pydatetime())
    update_destdb(destsession, 'cum_quantile', cum_df)
    
# 逐年收益
def yearly_quintile(destsession, session, factor_name, task_id, df):
    yearly_df = df
    n_bins = 5
    yearly_df['year'] = yearly_df['trade_date'].apply(lambda x : x.year)
    groupd = yearly_df.groupby('year')
    new_df = pd.DataFrame(columns=['q' + str(i) for i in range(1, n_bins+1)])
    for k, g in groupd:
        new_df.loc[k, :] = g[['q1','q2','q3','q4','q5']].sum()
    new_df['session'] = session
    new_df['factor_name'] = factor_name
    new_df['task_id'] = task_id
    new_df.index.name = 'year'
    new_df = new_df.reset_index()
    update_destdb(destsession, 'yearly_quantile',new_df)

## IC序列
def ic_serialize(destsession, session, factor_name, task_id, total_data):
    ic_series = total_data.groupby('trade_date').apply(lambda x: np.corrcoef(x['prc_factor'], x['dx'])[0, 1])
    ic_df = pd.DataFrame(ic_series,columns=['ic_values'])
    ic_df['session'] = session
    ic_df['factor_name'] = factor_name
    ic_df['task_id'] = task_id

    ic_df = ic_df.reset_index()
    ic_df['trade_date'] = ic_df['trade_date'].apply(lambda x : x.to_pydatetime())
    update_destdb(destsession, 'ic_serialize',ic_df)
    return ic_series
    
## 行业IR
def industry_ir(destsession, session, factor_name, task_id, total_data):
    industry_ic = total_data.groupby(['trade_date', 'industry']).apply(lambda x: np.corrcoef(x['prc_factor'], x['dx'])[0, 1])
    industry_ir = (industry_ic.groupby(level=1).mean() / industry_ic.groupby(level=1).std())
    industry_ir_df  = pd.DataFrame(industry_ir,columns=['ir_values'])
    industry_ir_df['session'] = session
    industry_ir_df['factor_name'] = factor_name
    industry_ir_df['task_id'] = task_id
    industry_ir_df.index.name='industry_name'
    industry_ir_df = industry_ir_df.reset_index()
    update_destdb(destsession, 'industry_ir',industry_ir_df)
    
def ic_decay(destsession, session, factor_name, task_id, total_data):
    max_shift = 5

    grouped_list = []
    grouped = total_data.groupby("code")
    for k, g in grouped:
        grouped_list.append([g,max_shift])
    
    '''
    cpus = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=cpus) as p:
        alpha_res = p.map(factor_shift, grouped_list)
    '''
    alpha_res = []
    for params in grouped_list:
        alpha_res.append(factor_shift(params))
        
    total_data = pd.concat(alpha_res).reset_index(drop=True)
    
    factor_names = ["prc_factor"]
    for i in range(1, max_shift+1):
        factor_names.append("prc_factor_l"+str(i))

    values = {}
    for f in factor_names:
        ic_series = total_data.groupby('trade_date').apply(lambda x: np.corrcoef(x[f], x['dx'])[0, 1])
        values[f] = ic_series.mean()
    values = pd.DataFrame(pd.Series(values))
    
    tvalues = values.T
    tvalues['session'] = session
    tvalues['factor_name'] = factor_name
    tvalues['task_id'] = task_id
    tvalues = tvalues.rename(columns={'prc_factor_l1':'l1','prc_factor_l2':'l2',
                               'prc_factor_l3':'l3','prc_factor_l4':'l4',
                               'prc_factor_l5':'l5','prc_factor':'l0'})
    update_destdb(destsession, 'ic_decay',tvalues)

def t_serialize(destsession, session, factor_name, task_id, neutralized_styles, cum_df, total_data):
    grouped = total_data.groupby('trade_date')
    fac_rets_ls_series = cum_df.q5 - cum_df.q1
    ## 回归法的因子收益
    fac_rets_list = []
    t_list = []

    # 加权最小二乘
    for k, g in grouped:
        X = g[["prc_factor"] + neutralized_styles]
        y = g[["dx"]]
        wts =np.sqrt(g[["negMarketValue"]])
        results = sm.WLS(y,X,weights=wts).fit()
        fac_rets_list.append(results.params[0])
        t_list.append(results.tvalues[0])

    fac_rets_series = pd.Series(fac_rets_list, index=fac_rets_ls_series.index)
    t_series = pd.Series(t_list, index=fac_rets_ls_series.index)
    t_df = pd.DataFrame(t_series.values, index = cum_df.trade_date, columns=['t_values']).reset_index()
    t_df['session'] = session
    t_df['factor_name'] = factor_name
    t_df['task_id'] = task_id
    update_destdb(destsession, 't_serialize',t_df)
    return fac_rets_series

def basic_info(destsession, session, factor_name, task_id, fac_rets_series,
               ic_series, cum_df, total_data, kwargs):
    #收益率
    fac_rets = fac_rets_series.cumsum().values[-1]

    #收益率t值
    fac_rets_ttest = ttest_1samp(fac_rets_series, 0)
    t_rets = fac_rets_ttest.statistic

    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    ic_marked = len(ic_series[ic_series.abs()>0.02])/len(ic_series)
    ir = ic_mean / ic_std

    #年化收益率
    annualized = cum_df.q0.values[-1] / len(cum_df.q0) * 250
    
    # 换手率
    last_code = None
    diff_count = 0
    sum_count = 0
    res = []
    grouped = total_data.groupby('trade_date')
    for k, g in grouped:
        er = g['prc_factor'].values
        g['group'] = quantile(er.flatten(), n_bins)
        res.append(g)
    turnover_df = pd.concat(res).reset_index()[['trade_date','code','group']]

    if df.q0.cumsum().values[-1] > df.q4.cumsum().values[-1]:
        group_df = turnover_df.set_index('group').loc[0].reset_index()
    else:
        group_df = turnover_df.set_index('group').loc[4].reset_index()
    grouped = group_df.groupby('trade_date')
    for k, g in grouped:
        if last_code is None:
            sum_count = len(g.code.values)
            last_code = g.code.values
        else:
            mix_code = set(g.code.values) & set(last_code)
            diff_count += (len(g.code.values) - len(mix_code))
            sum_count += len(g.code.values)
    turnover_rate = diff_count/sum_count
    
    basic_info = {'fac_rets':fac_rets,'t_rets':t_rets,'ic_mean':ic_mean,
             'ic_std':ic_std,'ic_marked':ic_marked,'ir':ir,
             'annualized':annualized,'turnover_rate':turnover_rate,
             'update_time':datetime.datetime.now(),'params':str(json.dumps(kwargs)),
             'remark':'中证500股票池'}
    
    basic_df = pd.DataFrame([basic_info])
    basic_df['session'] = session
    basic_df['factor_name'] = factor_name
    basic_df['task_id'] = task_id
    update_destdb(destsession, 'basic_info',basic_df)

@app.task
def factor_analysis(**kwargs):
    print(kwargs)
    db_info = kwargs['db_info']
    factor_name = kwargs['factor_name']
    neutralized_styles = kwargs["risk_styles"] + industry_styles
    start_date = kwargs['start_date']
    end_date = kwargs['end_date']
    universe_name = kwargs['universe_name']
    benchmark_code = kwargs['benchmark_code']
    freq = kwargs['freq']
    session = kwargs['session']
    
    ##写入数据库
    destination = sa.create_engine("mysql+mysqlconnector://quant:AUsYCJ4cMa@127.0.0.1:3306/quant")
    destsession = sessionmaker( bind=destination, autocommit=False, autoflush=True)

    task_id = str(int(time.time() * 1000000 + datetime.datetime.now().microsecond))
    
    
    engine = SqlEngine(db_info) # alpha-mind engine
    engine191 = create_engine(db_info, poolclass=NullPool)
    factors = fetch_factor(engine191, factor_name, start_date, end_date)
    ## factor_combination
    total_data = factor_combination(engine, factors, universe_name, start_date, end_date, freq)
    
    ## factor process
    total_data = factor_process(total_data, factor_name, neutralized_styles)
    
    ## 五分位收益
    cum_df = cum_quintile(total_data)
    
    ## 记录五分位和超额
    excess_quintile(destsession, session, factor_name, task_id, cum_df)
    
    ## 逐年收益
    yearly_quintile(destsession, session, factor_name, task_id, cum_df)
    
    ## IC序列
    ic_series = ic_serialize(destsession, session, factor_name, task_id, total_data)
    
    ## 行业IR
    industry_ir(destsession, session, factor_name, task_id, total_data)
    
    ## IC 半衰
    ic_decay(destsession, session, factor_name, task_id, total_data)
    
    ## T值序列
    fac_rets_series = t_serialize(destsession, session, factor_name, task_id, neutralized_styles,
                                  cum_df, total_data)
    
    ## 基本信息
    basic_info(destsession, session, factor_name, task_id, fac_rets_series,
               ic_series, cum_df, total_data, kwargs)
    return "任务结果"
    
    
    
    
    