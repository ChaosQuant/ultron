import pickle,itertools,sys,pdb
from ultron.factor.settlement.weighted import Weighted

# 读取数据
with open('total_data.pkl','rb') as file2:
    total_data = pickle.load(file2)
    
weight = Weighted()

industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']

risk_data = total_data[['code','trade_date'] + industry_styles + ['SIZE','COUNTRY']]

forward_returns  = total_data[['code','trade_date', 'ret']]

factor_data = total_data[['code','trade_date','CFinc1','ivr_day','roe_q','idl_mtm_20']]

print(weight.run(factor_data, risk_data, forward_returns, 'CFinc1'))