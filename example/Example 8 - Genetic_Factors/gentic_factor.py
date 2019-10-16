import pickle,itertools,sys,pdb,time
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import graphviz
from ultron.factor.genetic.geneticist.genetic import Gentic
from ultron.factor.fitness.weighted import Weighted
from ultron.factor.genetic.geneticist.operators import calc_factor
import multiprocessing
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
import warnings
warnings.filterwarnings("ignore")

'''
## IC 方法
def websim_weighted(factor_data, total_data, factor_sets):
    factor_data = factor_data.copy()
    factor_data = factor_data.reset_index().sort_values(['trade_date','code'])
    #此处ret放的位置不对，仅用于测试例
    factor_data = factor_data.fillna(0)
    score = np.corrcoef(factor_data['transformed'].values, total_data.sort_values(['trade_date','code'])['ret'].values)[0,1]
    return abs(score)
    
with open('factor_data.pkl','rb') as file2:
    total_data = pickle.load(file2)
'''

# return winsorized series
def se_winsorize(se, method='sigma', limits=(3.0, 3.0), drop=False):
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


# return standardized series
def se_standardize(se):
    try:
        res = (se - np.nanmean(se)) / np.nanstd(se)
    except:
        res = pd.Series(data=np.NaN, index=se.index)
    return res

## websim 方法
def websim_weighted(factor_data, total_data, factor_sets):
    factor_data = factor_data.copy()
    risk_data = total_data[['trade_date','code'] + industry_styles + ['SIZE']]
    forward_returns = total_data[['trade_date','code','ret']]
    weight = Weighted.create_weighted(method='onlylong')()
    stats = weight.run(factor_data=factor_data.reset_index(), 
                       risk_data=risk_data, forward_returns=forward_returns,
                       factor_name='transformed',horizon=5,default_value=np.iinfo(np.int32).min)
    if abs(stats['fitness']) > 0.554246 and stats['sharpe'] > 1.243449:
        score = abs(stats['fitness'])
    else:
        score = abs(stats['fitness']) / 100
    return abs(score)

def nan_rate(params):
    name = params['name']
    data = params['data']
    coverage_rate  =  1 - np.isnan(data).sum()/ len(data)
    return {'rate':coverage_rate,'name':name}

#读取数据
universe = 'hs300'
with open('./' + str(universe) + '_fac_results.pkl','rb') as file2:
    fac_results = pickle.load(file2)
    
with open('./' + str(universe) + '_factor_data.pkl','rb') as file2:
    factor_data = pickle.load(file2)

with open('./' + str(universe) + '_return_data.pkl','rb') as file2:
    return_data = pickle.load(file2)
    
with open('./' + str(universe) + '_risk_data.pkl','rb') as file2:
    risk_data = pickle.load(file2)
    
factor_sets = fac_results.factor_name.to_list()  
total_data = factor_data.merge(risk_data, on=['code', 'trade_date'])
risk_styles = [i for i in risk_data.columns if i not in ['trade_date','code']]
industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']

ndiff_field = ['trade_date','code','ret'] + risk_styles

total_data = total_data.sort_values(by=['trade_date','code'],ascending=True)

total_data = total_data.set_index('trade_date'
                                 ).loc[total_data.trade_date.unique()[0:20]].reset_index()

#数据处理
alpha_res = []
grouped = total_data.groupby(['trade_date'])
for k, g in grouped:
    f = pd.DataFrame()
    for factor_name in factor_sets:
        f[factor_name] = se_standardize(se_winsorize(g[factor_name].values)) # 去极值->标准化
    for k in ndiff_field:
        f[k] = g[k].values
    alpha_res.append(f)
alpha_data = pd.concat(alpha_res)

factor_data_list = []
for name in factor_sets:
    factor_data_list.append({'name':name,'data':alpha_data[name].values})
    
with multiprocessing.Pool(processes=4) as p:
    values_list = p.map(nan_rate, factor_data_list)
factor_rate = pd.DataFrame(values_list)
factor_rate = factor_rate[factor_rate.rate > 0.65]
alpha_data = alpha_data[list(factor_rate.name) + ndiff_field]

## 均值处理Nan
alpha_res = []
grouped = total_data.groupby(['trade_date'])
for k, g in grouped:
    f = pd.DataFrame()
    for factor_name in factor_sets:
        factor_data = g[factor_name].values
        factor_data[np.isnan(factor_data)] = factor_data[~np.isnan(factor_data)].mean()
        f[factor_name] =factor_data
    for k in ndiff_field:
        f[k] = g[k].values
    alpha_res.append(f)
standard_data = pd.concat(alpha_res)

#移动收益率
def shift_ret(data):
    data = data.sort_values(by='trade_date',ascending=True)
    data['ret'] = data['ret'].shift(-1)
    return data.dropna(subset=['ret'])

now_data = standard_data.groupby(['code']).apply(shift_ret)

standard_data = now_data.set_index('code').reset_index().sort_values(by=['trade_date','code'],ascending=True)

gentic = Gentic(population_size=100, tournament_size = 10, 
                init_depth=(4, 6),
                generations=4, n_jobs = 8, stopping_criteria=100, verbose=1,
                factor_sets = factor_sets,
                fitness=websim_weighted)


gentic.train(total_data=standard_data)
result = gentic._run_details

result_list = []
for program in result['best_programs'][-1]:
    result_list.append({'transform':program.transform(),
                       'fitness':program._raw_fitness})
    
with open('./result/' + str(int(time.time())) + str(universe) +  '_stm.pkl', 'wb') as f:
    pickle.dump([result_list], f)
