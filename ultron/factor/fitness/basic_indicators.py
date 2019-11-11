import numpy as np
import pandas as pd
from ultron.factor.combine.kutil import calc_ic
import pdb


class IC_Weighted(object):
    def __init__(self, result_type):
        self._result_type = result_type
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
    
    #中性化
    def neutralize(self, total_data, risk_df):
        se = total_data.dropna()
        # se = total_data.copy()
        risk = risk_df.loc[se.index,:]
        # use numpy for neu, which is faster
        x = np.linalg.lstsq(risk.values, np.matrix(se).T)[0]
        se_neu = se - risk.dot(x)[0]
    
        return se_neu
    
    #标准化
    def standardize(self, total_data):
        try:
            res = (total_data - np.nanmean(total_data)) / np.nanstd(total_data)
        except:
            res = pd.Series(data=np.NaN, index=total_data.index)
        return res
    
    
    def ic_calc(self, factor_data, forward_returns, risk_data, factor_name,
            risk_styles = None, method='quantile', up_limit=0.025, down_limit=0.025,
            return_col_name='nxt1_ret',ic_type='spearman'):
        factor_se = factor_data.set_index(['trade_date','code'])
        risk_se = risk_data.set_index(['trade_date','code'])
        forward_returns = forward_returns.set_index(['trade_date','code'])
        risk_styles = self._risk_styles if risk_styles is None else risk_styles
        risk_df = risk_se.reindex(factor_se.index)[self._industry_styles + risk_styles]
        risk_df.dropna(inplace=True)
        factor_se = factor_se.loc[risk_df.index][factor_name]
        returns = forward_returns.loc[risk_df.index]
        
        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.winsorize(x,
                                                                    method=method,
                                                                    limits=(up_limit, down_limit)))
        # factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.neutralize(x, risk_df)) # index 多了一项
        grouped = factor_se.groupby(level='trade_date')
        res = []
        for trade_date, g in grouped:
            neu = self.neutralize(g, risk_df)
            res.append(neu)
        factor_se = pd.concat(res, axis=0)
        factor_se = factor_se.groupby(level='trade_date').apply(lambda x: self.standardize(x)).reset_index().rename(columns={0:factor_name}).dropna()
        
        
        return calc_ic(factor_df=factor_se, return_df=returns, 
            factor_list=[factor_name], return_col_name=return_col_name, ic_type=ic_type)


    def run(self, factor_data, forward_returns, risk_data, factor_name,
            risk_styles = None, method='quantile', up_limit=0.025, down_limit=0.025,
            return_col_name='nxt1_ret',ic_type='spearman'):
        ic_serliaze = self.ic_calc(factor_data=factor_data,forward_returns=forward_returns,
                                  risk_data=risk_data,factor_name=factor_name,
                                  risk_styles=risk_styles,method=method,up_limit=up_limit,
                                  down_limit=down_limit,return_col_name=return_col_name,
                                  ic_type=ic_type)[factor_name].dropna()
        return ic_serliaze.values.mean() if self._result_type=='ic' else ic_serliaze.values.mean() / ic_serliaze.values.std()
