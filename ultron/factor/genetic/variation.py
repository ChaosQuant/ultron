# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import itertools,time,pdb
from . accumulators import accumulators_pool

##构造5个算子
#accumulators = {2:np.log,3:np.sqrt,4:np.fabs}


class GeneticMutationFactors(object):
    
    def __init__(self, del_prob, add_prob, change_prob, conver_prob,
                 generation=500, group_num=10,
                objective=None):
        self._del_prob = del_prob # 删除原始特征概率
        self._add_prob = add_prob # 添加新特征概率
        self._change_prob =  change_prob #变异概率
        self._conver_prob = conver_prob # 收敛差值
        self._generations = generation
        self._group_num = group_num
        self._objective = objective
        
    # 初代种群生成
    def ga_generate_ori(self, ori_field, add_field):
        ## 选取原始特征过程
        ori_list = (np.random.uniform(0, 1, (1, len(ori_field))) < self._del_prob).tolist()[0]
        add_list = (np.random.uniform(0, 1, (1, len(add_field))) < self._add_prob).tolist()[0]
        new_list = ori_list + add_list
        new_list = [1 if i> 0 else 0 for i in new_list]
        return np.array(new_list)
    
    ## 交叉变异过程
    def ga_cross_next_group(self, ori_group, dict_score = 'ori', generation=0):
        new_dict = ori_group.copy()
        if generation == 0:
            score = 1.0 / len(ori_group)
            dict_score = {k:score for k in ori_group.keys()}
        g, p = np.array([[k, v] for k, v in dict_score.items()]).T
        flag = max(ori_group.keys())
        cross_group = np.random.choice(g, size = int(len(g)/2), p = p, replace= False)
        for (fa,mo) in itertools.combinations(cross_group, 2):
            flag += 1
            fa_code, mo_code = ori_group[fa], ori_group[mo]
            cut_point = np.random.randint(1, len(fa_code)-1)
            fa_code0, fa_code1 = fa_code[:cut_point], fa_code[cut_point:]
            mo_code0, mo_code1 = mo_code[:cut_point], mo_code[cut_point:]
            new1 = np.hstack([fa_code0, mo_code1])
            prob = np.random.uniform(0, 1)
            if prob < self._change_prob:
                change_point = np.random.randint(0, len(fa_code))
                ## 改变该点的值
                new1[change_point] = not new1[change_point] 
                #所有的显性特征进行随机变异
                new1 = [int(np.random.uniform(1, len(accumulators_pool) + 1)) if i> 0 else 0 for i in new1] 
            new_dict[flag] = np.array(new1)
        return new_dict
    
    #种群特征计算
    def calc_evalue_group(self, sub_group, evalue_cols, total_data):
        index = 0
        res = {}
        cols = []
        for i in sub_group:
            if i > 0:
                factor_name = evalue_cols[index]
                if i > 1:
                    alpha_start_time = time.time()
                    accumulator = accumulators_pool[i](str(factor_name))
                    factor_data = accumulator.transform(total_data[[str(factor_name),'code',
                                                        'trade_date']].set_index('trade_date'), 
                                                         category_field='code', dropna=False)
                    factor_data = factor_data['transformed']
                else:
                    factor_data = total_data[factor_name].copy()
                res[factor_name + 'c_' + str(i)] = factor_data.fillna(0).values
                cols.append(factor_name + 'c_' + str(i))
            index += 1
        return cols, res
    
    ## 种群个体能力评价
    def ga_evalue_group(self, sub_group, total_data, evalue_cols, diff_filed):
        tres = {} # # 新种群有变异后的特征也有父类特征
        score_dict = {}
        cols_dict = {}
        for g, code in sub_group.items():
            cols, res = self.calc_evalue_group(sub_group[g], evalue_cols, total_data)
            #合并其他特征
            sub_data = pd.DataFrame(res)
            for diff in diff_filed:
                sub_data[diff] = total_data[diff]
            score = self._objective(sub_data, cols)
            score_dict[g] = score
            cols_dict[g] = cols
            tres = dict(tres, **res)
        return pd.DataFrame(tres), score_dict, cols_dict
    
    #种群变异
    def ga_kill_group(self, total_data, ori_group, dict_score, evalue_cols, diff_filed, generation = 0):
        """
        total_data 种群数据集
        ori_group  有效种群特征组
        dict_score 分数
        evalue_cols 种群特征
        """
        # 生成新一代特征
        sub_group = self.ga_cross_next_group(ori_group, dict_score=dict_score,generation=generation)
        # 生成对应数据
        sub_data, score_dict, cols_dict = self.ga_evalue_group(sub_group, total_data, evalue_cols, diff_filed)
        score_se = pd.Series(score_dict)
        print('种群数%d, 种群均分:%f'%(len(score_se),score_se.mean()))
        fact_se = score_se.sort_values(ascending=False)[:self._group_num] 
        score_se = score_se.sort_values(ascending=False)[:self._group_num] / (
            score_se.sort_values(ascending= False)[:self._group_num].sum())
        
        sub_data = pd.concat([sub_data,total_data[diff_filed]],
                         axis=1)
        liv_group = {}
        for k in score_se.keys():
            liv_group[k] = np.array([1 if i in cols_dict[k] else 0 for i in np.array(sub_data.columns)])
        return sub_data, liv_group,  score_se,  dict(fact_se), np.array(sub_data.columns), cols_dict
        
    def genetic_run(self, total_data, diff_filed, factors_filed = None, 
                    strong_field = None, weak_field = None):
        if factors_filed is not None:
            point = int(np.random.uniform(0, len(factors_filed))/2)
            ori_field = factors_filed[:point]
            add_field = factors_filed[point:]
        elif strong_field is not None and weak_field is not None:
            ori_field = strong_field
            add_field = weak_field
        evalue_cols = np.array(ori_field + add_field)
        last_score = 0.0
        #初始种群
        ori_group = {i:self.ga_generate_ori(ori_field, add_field) for i in range(self._group_num)}
        for i in range(self._generations):
            
            if i == 0:
                sub_data, liv_group, score_se, fact_se, cols, cols_dict = self.ga_kill_group(
                    total_data, ori_group, 'ori', evalue_cols, diff_filed, 0)
            else:
                sub_data, liv_group, score_se, fact_se, cols, cols_dict = self.ga_kill_group(
                    sub_data, liv_group, score_se, cols, diff_filed, 1)
            best_fact_score = pd.Series(fact_se).sort_values()[-1:]
            best_score = pd.Series(fact_se).sort_values()
            diff_fact_score = best_score.values[0] - last_score
            diff_score = best_score[-1:].values[0] - best_score[0:1].values[0]
            print('繁衍代数:%d,最好分数:%f,%d和%d最好组分数差值%f,%d代最好最差种群分数差值%f'%((i+1),
              (best_score.values[0] if best_score.values[0] > last_score else last_score),
               i+1,i,diff_fact_score,i+1,diff_score)) 
            if diff_fact_score < self._conver_prob and diff_score < self._conver_prob:
                break
            last_score = best_score.values[0]
            
        best_code = pd.Series(fact_se).sort_values()[-1:].index[0]
        best_list = liv_group[best_code]
        best_field = cols[[True if i> 0 else False for i in best_list]]
        return best_code, best_field
        