import pandas as pd
import numpy as np
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
import pickle,itertools,sys,pdb
import warnings
warnings.filterwarnings("ignore")
#sys.path.append('../..')
from ultron.factor.combine.combine_engine import CombineEngine
from ultron.factor.genetic.mutation_factors import GeneticMutationFactors


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
    total_data['conmbine'] = total_data[factor_list].mean(axis=1).values
    score = np.corrcoef(total_data['conmbine'].fillna(0).values, total_data['ret'].fillna(0).values)[0,1]
    return abs(score)
    #return np.random.uniform(0, 1, 1)[0]


mutation_factors = GeneticMutationFactors(0.6, 0.2, 0.9, 0.0000001, generation=6, group_num=5, objective=equal_combine)

with open('factor_data.pkl','rb') as file2:
    total_data = pickle.load(file2)
    
diff_filed = ['trade_date','code','ret']
factor_columns = [i for i in list(set(total_data.columns)) if i not in ['trade_date','code','ret']]

point = int(np.random.uniform(0, len(factor_columns))/2)
ori_field = factor_columns[:point]
add_field = factor_columns[point:]

best_code, best_field = mutation_factors.genetic_run(total_data, diff_filed = diff_filed, strong_field = ori_field, 
                             weak_field = add_field)
print(best_code)
print('----')
print(best_field)
