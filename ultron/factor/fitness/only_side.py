import os,time, pdb
import datetime as dt
import sqlalchemy
import numpy as np
import pandas as pd
import statsmodels.api as sm

class OnlySideWeighted(object):
    def __init__(self):
        self._industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']
        self._risk_styles = ['BETA','MOMENTUM','SIZE','EARNYILD','RESVOL','GROWTH','BTOP',
                             'LEVERAGE','LIQUIDTY','SIZENL']
        
    #暂时写此处，去极值
    def winsorize(self, total_data, method='sigma', limits=(3.0, 3.0), drop=True):
        se = total_data.copy()
        if method == 'quantile':
            down, up = se.quantile([limits[0], 1.0 - limits[1]])
        elif method == 'sigma':
            std, mean = se.std(), se.mean()
            down, up = mean - limits[0]*std, mean + limits[1]*std
        
        if drop:
            se[se<down] = np.NaN
            se[se>up] = np.NaN
        else:
            se[se<down] = down
            se[se>up] = up
        return se
    
    #标准化
    def standardize(self, total_data):
        try:
            res = (total_data - np.nanmean(total_data)) / np.nanstd(total_data)
        except:
            res = pd.Series(data=np.NaN, index=total_data.index)
        return res
    
    #中性化
    def neutralize(self, total_data, risk_df):
        se = total_data.dropna()
        # se = total_data.copy()
        risk = risk_df.loc[se.index,:]
        # use numpy for neu, which is faster
        x = np.linalg.lstsq(risk.values, np.matrix(se).T)[0]
        se_neu = se - risk.dot(x)[0]
    
        return se_neu

    def top_equal_weights(self, group, top='top', top_pct=0.2):
        if top == 'bottom':
            group = -1.0 * group
        group = group.rank(pct=True)
        group[group < 1.0-top_pct] = 0.0
        group[group >= 1.0-top_pct] = 1.0 / len(group[group >= 1.0-top_pct])
        return group
    
    def calc_stats(self, returns_df):
        # 总体指标
        returns_se, turnover_se = returns_df['returns'], returns_df['turnover']

        ir = returns_se.mean() / returns_se.std()
        sharpe = np.sqrt(252) * ir
        turnover = turnover_se.mean()
        returns = returns_se.sum() * 252 / len(returns_se)
        fitness = sharpe * np.sqrt(abs(returns) / turnover)
        margin = returns_se.sum() / turnover_se.sum()
        stats_se = pd.Series({'status':1, 'ir': ir, 'sharpe': sharpe, 'turnover': turnover, 
                              'returns': returns, 'fitness': fitness, 'margin': margin})
        return stats_se

    def returns(self, factor_se, forward_returns, init_capital=100000):
        # 超额收益，此处benchmark采用全股票池算数均值
        forward_excess_returns = forward_returns.groupby(level=['trade_date']).apply(
            lambda x: x - x.mean())
        res_dict = {}
        for top in ['top', 'bottom']:
            weights = factor_se.groupby(level=['trade_date']).apply(lambda x: self.top_equal_weights(x, top=top, top_pct=0.2))
            weighted_returns = forward_excess_returns.multiply(weights, axis=0)
            factor_ret_se = weighted_returns.groupby(level='trade_date').sum()
            turnover_se = weights.unstack().diff().abs().sum(axis=1)
            res_dict[top] = pd.DataFrame({'returns': factor_ret_se, 'turnover': turnover_se})
        return res_dict
    
    def run(self, factor_data, risk_data, forward_returns, default_value,
            factor_name, horizon=1, method='quantile', up_limit=0.025, down_limit=0.025,
            init_capital=100000):
        """
        参数：
            horizon: 调仓期，按照交易日计算。
        """
        factor_se = factor_data.set_index(['trade_date','code'])
        risk_se = risk_data.set_index(['trade_date','code'])
        forward_returns = forward_returns.set_index(['trade_date','code'])
        risk_df = risk_se.reindex(factor_se.index)[self._industry_styles + ['SIZE']]
        risk_df.dropna(inplace=True)
        factor_se = factor_se.loc[risk_df.index][factor_name]
        returns = forward_returns.loc[risk_df.index]
        
        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.winsorize(x,
                                                                    method=method,
                                                                    limits=(up_limit, down_limit)))
        grouped = factor_se.groupby(level='trade_date')
        res = []
        for trade_date, g in grouped:
            neu = self.neutralize(g, risk_df)
            res.append(neu)
        factor_se = pd.concat(res, axis=0)
        
        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.standardize(x))
        
        #判读覆盖率低于某个阈值直接设置无效
        cover_rate = 1 - len(factor_se[np.isnan(factor_se.values)]) / len(factor_se)
        if cover_rate < 0.75:
            return {'status':0, 'fitness':default_value}
        # top 20% 等权方法计算的因子收益数据
        res_dict = self.returns(factor_se, forward_returns['ret'])
        
        #计算指标
        stats_df = pd.DataFrame({x: self.calc_stats(res_dict[x]) for x in res_dict.keys()})
        if stats_df.top.returns > stats_df.bottom.returns and stats_df.top.returns > 0:
            return stats_df.top.to_dict()
        elif stats_df.bottom.returns > stats_df.top.returns and stats_df.bottom.returns > 0:
            return stats_df.bottom.to_dict()
        else:
            return {'status':0, 'fitness':default_value}