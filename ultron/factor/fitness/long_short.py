import os,time, pdb
import datetime as dt
import sqlalchemy
import numpy as np
import pandas as pd
import statsmodels.api as sm

class LongShortWeighted(object):
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
            res = (total_data - total_data.mean()) / total_data.std()
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

    def _to_weights(self, group):
        demeaned_vals = group - group.mean()
        return demeaned_vals / demeaned_vals.abs().sum()
    
    
    def _to_ls_count(self, group, long=True):
        demeaned_vals = group - group.mean()
        if long:
            count = len(demeaned_vals[demeaned_vals>0])
        else:
            count = len(demeaned_vals[demeaned_vals<0])
        return count
    
    def returns(self, total_data, forward_returns, init_capital=100000):
        weights = total_data.groupby(level=['trade_date']).apply(self._to_weights)
        weighted_returns = forward_returns.multiply(weights, axis=0)
        
        factor_ret = weighted_returns.groupby(level='trade_date').sum()
        pnl = init_capital*2*factor_ret
        turnover = weights.unstack().T.diff().abs().sum(axis=1)
        long_count = total_data.groupby(level=['trade_date']).apply(self._to_ls_count)
        short_count = total_data.groupby(level=['trade_date']).apply(lambda x: self._to_ls_count(x, long=False))
        return factor_ret, pnl, turnover, long_count, short_count
    
    def run(self, factor_data, risk_data, forward_returns,
            factor_name, horizon=1, method='quantile', up_limit=0.025, down_limit=0.025,
            init_capital=100000):
        """
        参数：
            horizon: 调仓期，按照交易日计算。
        """
        factor_se = factor_data.set_index(['code','trade_date'])
        risk_se = risk_data.set_index(['code','trade_date'])
        forward_returns = forward_returns.set_index(['code','trade_date'])
        # risk_df = risk_se.reindex(factor_se.index)[self._industry_styles + ['SIZE'] + ['COUNTRY']]
        risk_df = risk_se.reindex(factor_se.index)[self._industry_styles + ['SIZE']]
        risk_df.dropna(inplace=True)
        factor_se = factor_se.loc[risk_df.index][factor_name]
        returns = forward_returns.loc[risk_df.index]
        
        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.winsorize(x, method=method,
                                                                    limits=(up_limit, down_limit)))
        # factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.neutralize(x, risk_df)) # index 多了一项
        grouped = factor_se.groupby(level='trade_date')
        res = []
        for trade_date, g in grouped:
            neu = self.neutralize(g, risk_df)
            res.append(neu)
        factor_se = pd.concat(res, axis=0)

        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.standardize(x))
        
        factor_ret, pnl, turnover_se, lc, sc = self.returns(factor_se, forward_returns['ret'], init_capital=init_capital)
        
        #计算指标
        ir = factor_ret.mean()/factor_ret.std()
        sharpe = np.sqrt(252/horizon)*ir
        turnover = turnover_se.mean()
        returns = factor_ret.sum()*252/horizon/len(factor_ret)
        fitness = sharpe * np.sqrt(abs(returns)/turnover)
        margin = factor_ret.sum()/turnover_se.sum()
        
        capital = pnl + init_capital
        running_max = np.maximum.accumulate(capital)
        drawback_data = -((running_max - capital) / running_max)
        max_drawdown = np.min(drawback_data)
        
        return {'ir':ir, 'sharpe':sharpe, 'turnover':turnover, 'returns':returns, 
                'fitness':fitness, 'margin':margin, 'max_drawdown':max_drawdown}