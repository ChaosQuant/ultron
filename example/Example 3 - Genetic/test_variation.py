import pandas as pd
import numpy as np
import sys
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
from ultron.factor.combine.combine_engine import CombineEngine
#from ultron.factor.genetic.mutation_factors import GeneticMutationFactors
from ultron.factor.genetic.cross_factors import GeneticCrossFactors
import pickle,itertools,sys,pdb
import warnings
warnings.filterwarnings("ignore")

# 以等权合成因子的IC值作为分数判断 (注意:系统是以分数倒序排序来进行种群筛选，若类似IC带有方向性需转化为绝对值)
def equal_combine(factor_df, factor_list):
    factor_df = factor_df.copy()
    ndiff_field = [i for i in list(set(factor_df.columns)) if i not in factor_list]
    #合成前数据预处理
    alpha_res = []
    grouped = factor_df.groupby(['trade_date'])
    for k, g in grouped:
        ret_preprocess = factor_processing(g[factor_list].fillna(0).values,
                                       pre_process=[winsorize_normal, standardize])
        f = pd.DataFrame(ret_preprocess, columns=factor_list)
        for k in ndiff_field:
            f[k] = g[k].values
        alpha_res.append(f)
    total_data = pd.concat(alpha_res)
    total_data = factor_df
    total_data['conmbine'] = total_data[factor_list].mean(axis=1).values
    score = np.corrcoef(total_data['conmbine'].fillna(0).values, total_data['ret'].fillna(0).values)[0,1]
    #score = abs(total_data['conmbine'].mean()) / 100
    return abs(score)

pdb.set_trace()
mutation_factors = GeneticCrossFactors(del_prob=0.4, add_prob=0.2, cross_prob=0.4, change_prob=0.9, 
                                       conver_prob=0.0000001, generation=30, group_num=10, objective=equal_combine)

with open('factor_data.pkl','rb') as file2:
    total_data = pickle.load(file2)
    
total_data = total_data.sort_values(by=['trade_date','code'],ascending=True)

diff_filed = ['trade_date','code','ret']
factor_columns = [i for i in list(set(total_data.columns)) if i not in ['trade_date','code','ret']]

#所有因子数据做去极值和标准化处理
alpha_res = []
grouped = total_data.groupby(['trade_date'])
for k, g in grouped:
    ret_preprocess = factor_processing(g[factor_columns].fillna(0).values,
                                       pre_process=[winsorize_normal, standardize])
    f = pd.DataFrame(ret_preprocess, columns=factor_columns)
    for k in diff_filed:
        f[k] = g[k].values
    alpha_res.append(f)
total_data = pd.concat(alpha_res)

point = int(np.random.uniform(0, len(factor_columns))/2)
ori_field = factor_columns[:point]
add_field = factor_columns[point:]

#best_code, best_field
best_code, best_field = mutation_factors.genetic_run(total_data, diff_filed = diff_filed, strong_field = ori_field, 
                             weak_field = add_field,is_best=False)
print(best_code)
print('----')
print(best_field)
