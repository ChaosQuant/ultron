# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle
import pickle,itertools,sys,pdb
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
from ultron.factor.combine.combine_engine import CombineEngine
from ultron.factor.genetic.mutation_factors import GeneticMutationFactors
from ultron.factor.settlement.weighted import Weighted
from ultron.factor.genetic.accumulators import transform
from ultron.utilities.mlog import MLog
import warnings
warnings.filterwarnings("ignore")

## websim 方法
def websim_weighted(factor_df, factor_list):
    total_data = factor_df.copy()
    risk_data = total_data[['code','trade_date'] + industry_styles + ['SIZE']]
    forward_returns  = total_data[['code','trade_date', 'ret']]
    factor_data = total_data[factor_list]
    
    #等权合成
    ndiff_field = [i for i in list(set(total_data.columns)) if i not in factor_list]
    #合成前数据预处理
    alpha_res = []
    grouped = total_data.groupby(['trade_date'])
    for k, g in grouped:
        ret_preprocess = factor_processing(g[factor_list].fillna(0).values,
                                       pre_process=[winsorize_normal, standardize])
        f = pd.DataFrame(ret_preprocess, columns=factor_list)
        for k in ndiff_field:
            f[k] = g[k].values
        alpha_res.append(f)
    alpha_data = pd.concat(alpha_res)
    alpha_data['conmbine'] = alpha_data[factor_list].mean(axis=1).values
    weight = Weighted()
    stats = weight.run(alpha_data, risk_data, forward_returns, 'conmbine')
    if abs(stats['fitness']) > 0.554246 and stats['sharpe'] > 1.243449:
        score = abs(stats['fitness'])
    else:
        score = abs(stats['fitness']) / 100
    return abs(score)

pdb.set_trace()

MLog().config(name='console_websim')
MLog().write().info('----')
#读取数据
with open('./demo/fac_results.pkl','rb') as file2:
    fac_results = pickle.load(file2)
    
with open('./demo/factor_data.pkl','rb') as file2:
    factor_data = pickle.load(file2)

with open('./demo/return_data.pkl','rb') as file2:
    return_data = pickle.load(file2)
    
with open('./demo/risk_data.pkl','rb') as file2:
    risk_data = pickle.load(file2)
    
    
stdup_factor = fac_results[(fac_results['sharpe'] > 1.243449) & (fac_results['fitness'] > 0.554246)]

stddown_factor = fac_results[~((fac_results['sharpe'] > 1.243449) & (fac_results['fitness'] > 0.554246))]

up_ori = list(stdup_factor['factor_name'])
down_ori = list(stddown_factor['factor_name'])

total_data = factor_data.merge(risk_data, on=['code', 'trade_date'])

ori_field = up_ori
add_field = down_ori
risk_styles = [i for i in risk_data.columns if i not in ['trade_date','code']]
industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']

diff_filed = ['trade_date','code','ret'] + risk_styles
# 非因子列
total_data = total_data.sort_values(by=['trade_date','code'],ascending=True)

# 定义遗传对象
mutation_factors = GeneticMutationFactors(del_prob=0.85, #删除强特征概率
                                          add_prob=0.05, #添加弱特征概率
                                          change_prob=0.9, #突变概率
                                          cover_prob = 0.02, # 种群变异覆盖率
                                          conver_prob=0.00001,#收敛值大小，即子代最好种群和父代最好种群分数差值，若小于改值则停止繁衍
                                          generation=6, # 繁衍代数
                                          group_num=10, # 每代种群数
                                          objective=websim_weighted)

#第一种返回最后一代最好前group_num种群
field_group = mutation_factors.genetic_run(total_data, diff_filed = diff_filed, strong_field = ori_field, 
                             weak_field = add_field, is_best=False)


formula_group = {}
for k, g in field_group.items():
    formula_group[k] = [transform(i,is_formula=False) for i in g]


#参数集
pamram_sets={'del_prob':0.8, 'add_prob':0.2,
            'change_prob':0.9,'conver_prob':0.00001,
            'generation':100, 'group_num':20}

with open('stm.pk', 'wb') as f:
    pickle.dump([pamram_sets, formula_group], f)
