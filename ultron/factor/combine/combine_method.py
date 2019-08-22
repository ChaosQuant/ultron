# -*- coding: utf-8 -*-

# 列名: 股票代码 code, 日期 trade_date
import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as st
import statsmodels.api as sm 
import seaborn
from sklearn.covariance import LedoitWolf
from cvxopt import matrix, solvers
from . kutil import calc_ic

def factor_combine(factor_df, factor_list, weight_df):
    """
    因子合成
    参数:
        factor_df: DataFrame, 待合成因子值
        factor_list: list, 待合成因子列表
        weight_df:　DataFrame, 因子权重
    返回:
        DataFrame, 复合因子
    """
    factor_df = factor_df.dropna(subset=factor_list, how='all')
    
    merge_df = factor_df.merge(weight_df, on=['trade_date'], suffixes=('', '_w'))
    
    w_list = [fn+'_w' for fn in factor_list]
    merge_df[w_list] = np.where(merge_df[factor_list].isnull(), 0, merge_df[w_list])
    merge_df['combine'] = np.sum(merge_df[factor_list].fillna(0).values*merge_df[w_list].values, axis=1)
    merge_df['combine'] = merge_df['combine']/merge_df[w_list].abs().sum(axis=1)
    
    return merge_df[['code', 'trade_date', 'combine']]

def equal_combine(factor_df, factor_list, ):
    """
    等权法合成因子
    参数:
        factor_df: DataFrame, 待合成因子值
        factor_list: list, 待合成因子列表
    返回:
        DataFrame, 复合因子
    """
    factor_df = factor_df.copy()
    return factor_df[factor_list].mean(axis=1).values
    #factor_df['equal']= factor_df[factor_list].mean(axis=1)
    #return factor_df[['code', 'trade_date', 'equal']]


def hist_ret_combine(factor_df, mret_df, factor_list, size_indu_df, indu_list,
                     span, method='equal', half_life=1):
    """
    历史收益率加权法合成因子
    参数:
        factor_df: DataFrame, 待合成因子值
        mret_df: DataFrame, 个股收益率
        factor_list: list, 待合成因子列表
        span: 使用历史长度计算历史收益率均值
        method: 历史收益率均值计算方法。'equal':算术平均；'half_life':半衰加权
        half_life: int, 半衰加权时的半衰期
    返回:
        DataFrame, 复合因子
    """
    merged_df = factor_df.merge(size_indu_df, on=['code', 'trade_date']).merge(mret_df, on=['code', 'trade_date'])
    merged_df = merged_df.dropna(subset=['nxt1_ret'])
    # 计算历史因子收益率
    hist_ret = []
    for fn in factor_list:
        tmp = merged_df.groupby('trade_date').apply(lambda df: sm.OLS(df['nxt1_ret'], sm.add_constant(df[[fn, 'SIZE']+indu_list]), missing='drop').fit().params[1])
        hist_ret.append(tmp)
    hist_ret = pd.concat(hist_ret, axis=1)
    hist_ret.columns = factor_list
    hist_ret = hist_ret.reset_index().sort_values('trade_date')
    hist_ret['trade_date'] = hist_ret['trade_date'].shift(-1)
    
    # 计算历史因子收益率移动平均
    for fn in factor_list:
        if method == 'equal':
            hist_ret[fn+'_ma'] = hist_ret[fn].rolling(span).mean()
        elif method == 'half_life':
            hist_ret[fn+'_ma'] = hist_ret[fn].rolling(span).apply(lambda x: np.average(x, weights=list(reversed([0.5**(1.0*i/half_life) for i in range(span)]))))
        else:
            return 0
    
    hist_ret = hist_ret.dropna()
    hist_ret = hist_ret.drop(factor_list, axis=1)
    hist_ret.columns = ['trade_date']+factor_list
    
    # 因子加权
    conb_df = factor_combine(factor_df, factor_list, hist_ret)
    return conb_df, hist_ret


def hist_ic_combine(factor_df, mret_df, factor_list, span, method='equal', half_life=1):
    """
    历史收IC加权法合成因子
    参数:
        factor_df: DataFrame, 待合成因子值
        mret_df: DataFrame, 个股收益率
        factor_list: list, 待合成因子列表
        span: 使用历史长度计算历史收益率均值
        method: 历史IC均值计算方法。'equal':算术平均；'half_life':半衰加权
        half_life: int, 半衰加权时的半衰期
    返回:
        DataFrame, 复合因子
    """
    # 计算各期IC
    ic_df = calc_ic(factor_df, mret_df, factor_list, return_col_name='nxt1_ret', ic_type='spearman')
    ic_df = ic_df.sort_values('trade_date')
    ic_df['trade_date'] = ic_df['trade_date'].shift(-1)
    
    # 计算历史因子收益率移动平均
    for fn in factor_list:
        if method == 'equal':
            ic_df[fn+'_ma'] = ic_df[fn].rolling(span).mean()
        elif method == 'half_life':
            ic_df[fn+'_ma'] = ic_df[fn].rolling(span).apply(lambda x: np.average(x, weights=list(reversed([0.5**(1.0*i/half_life) for i in range(span)]))))
        else:
            return 0
    
    ic_df = ic_df.dropna()
    ic_df = ic_df.drop(factor_list, axis=1)
    ic_df.columns = ['trade_date']+factor_list
    
    # 因子加权
    conb_df = factor_combine(factor_df, factor_list, ic_df)
    return conb_df, ic_df

def max_icir_combine(factor_df, mret_df, factor_list, span, method='sample', weight_limit=True):
    """
    最大化ICIR加权法合成因子
    参数:
        factor_df: DataFrame, 待合成因子值
        mret_df: DataFrame, 个股收益率
        factor_list: list, 待合成因子列表
        span: 使用历史长度计算IC均值和协方差矩阵
        method: 估计协方差矩阵的方法。'sample':直接用样本协方差矩阵；'shrunk':压缩估计
        weight_limit: bool, 是否约束权重为正
    返回:
        DataFrame, 复合因子
    """
    # 计算各期IC
    ic_df = calc_ic(factor_df, mret_df, factor_list, return_col_name='nxt1_ret', ic_type='spearman')
    ic_df = ic_df.sort_values('trade_date')
    ic_df['trade_date'] = ic_df['trade_date'].shift(-1)
    ic_df = ic_df.dropna()
    
    # 最大化ICIR
    m_ir_df = {}
    for i in range(span-1, len(ic_df)):
        dt = ic_df.ix[i, 'trade_date']
        ic_dt = ic_df.ix[i-span+1:i, factor_list]

        n = len(factor_list)
        # 求解最优化问题
        if method == 'sample':
            P = matrix(2*np.cov(ic_dt.T))
        elif method == 'shrunk':
            P = matrix(2*LedoitWolf().fit(ic_dt[factor_list].as_matrix()).covariance_)
        q = matrix([0.0]*n)
        G = matrix(-np.identity(n))
        h = matrix([0.0]*n)
        A = matrix(ic_dt.mean(), (1,n))
        b = matrix(1.0)
        if weight_limit:
            try:
                res = np.array(solvers.qp(P=P,q=q,G=G,h=h, A=A,b=b)['x'])
            except:
                res = np.array(solvers.qp(P=P,q=q, A=A,b=b)['x'])
        else:
            res = np.array(solvers.qp(P=P,q=q, A=A,b=b)['x'])

        m_ir_df[dt] = np.array(res).reshape(n)
    m_ir_df = pd.DataFrame(m_ir_df, index=factor_list).T.reset_index()
    if weight_limit:
        m_ir_df[factor_list] = np.where(m_ir_df[factor_list] < 0, 0, m_ir_df[factor_list])
    m_ir_df.loc[m_ir_df.sum(axis=1)==0, factor_list] = 1 
    m_ir_df.columns = ['trade_date']+factor_list
    
    # 因子加权
    conb_df = factor_combine(factor_df, factor_list, m_ir_df)
    return conb_df, m_ir_df

def max_ic_combine(factor_df, mret_df, factor_list, span, method='sample', weight_limit=True):
    """
    最大化IC加权法合成因子
    参数:
        factor_df: DataFrame, 待合成因子值
        mret_df: DataFrame, 个股收益率
        factor_list: list, 待合成因子列表
        span: 使用历史长度计算IC均值
        method: 估计协方差矩阵的方法。'sample':直接用样本协方差矩阵；'shrunk':压缩估计
        weight_limit: bool, 是否约束权重为正
    返回:
        DataFrame, 复合因子
    """
    # 计算各期IC
    ic_df = calc_ic(factor_df, mret_df, factor_list, return_col_name='nxt1_ret', ic_type='spearman')
    ic_df = ic_df.sort_values('trade_date')
    ic_df['trade_date'] = ic_df['trade_date'].shift(-1)
    for fn in factor_list:
        ic_df[fn] = ic_df[fn].rolling(span).mean()
    ic_df = ic_df.dropna()
    
    # 最大化IC
    m_ic_df = {}
    for dt in ic_df['trade_date']:
        ic_mean = ic_df.loc[ic_df['trade_date'] == dt, factor_list].values
        tmp_factor_df = factor_df.loc[factor_df['trade_date'] == dt, factor_list]

        n = len(factor_list)
        # 求解最优化问题
        if method == 'sample':
            P = matrix(2*np.cov(tmp_factor_df.T))
        elif method == 'shrunk':
            P = matrix(2*LedoitWolf().fit(tmp_factor_df.dropna().as_matrix()).covariance_)
        q = matrix([0.0]*n)
        G = matrix(-np.identity(n))
        h = matrix([0.0]*n)
        A = matrix(ic_mean, (1,n))
        b = matrix(1.0)
        if weight_limit:
            try:
                res = np.array(solvers.qp(P=P,q=q,G=G,h=h, A=A,b=b)['x'])
            except:
                res = np.array(solvers.qp(P=P,q=q, A=A,b=b)['x'])
        else:
            res = np.array(solvers.qp(P=P,q=q,A=A,b=b)['x'])

        m_ic_df[dt] = np.array(res).reshape(n)
    m_ic_df = pd.DataFrame(m_ic_df, index=factor_list).T.reset_index()
    if weight_limit:
        m_ic_df[factor_list] = np.where(m_ic_df[factor_list] < 0, 0, m_ic_df[factor_list])
    m_ic_df.loc[m_ic_df.sum(axis=1)==0, factor_list] = 1 
    m_ic_df.columns = ['trade_date']+factor_list
    
    # 因子加权
    conb_df = factor_combine(factor_df, factor_list, m_ic_df)
    return conb_df, m_ic_df