# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import itertools
import pdb

class GeneticFactors(object):
    
    def __init__(self, del_prob, add_prob, change_prob, generations,
                 group_num, sub_num, objective):
        self._del_prob = del_prob # 删除原始特征概率
        self._add_prob = add_prob # 添加新特征概率
        self._change_prob =  change_prob
        self._generations = generations
        self._sub_num = sub_num
        self._group_num = group_num
        self._objective  = objective 
        
    def reset_params(self, del_prob, add_prob, change_prob, generations):
        self._del_prob = del_prob # 删除原始特征概率
        self._add_prob = add_prob # 添加新特征概率
        self._change_prob =  change_prob
        self._generations = generations
        
    # 初代种群生成
    def ga_generate_ori(self, ori_field, add_field):
        ## 选取原始特征过程
        ori_list = (np.random.uniform(0, 1, (1, len(ori_field))) < self._del_prob).tolist()[0]
        add_list = (np.random.uniform(0, 1, (1, len(add_field))) < self._add_prob).tolist()[0]
        new_list = ori_list + add_list
        return np.array(new_list)
    
    # 交叉变异过程
    def ga_cross_next_group(self, ori_group, dict_score = 'ori'):
        new_dict = ori_group.copy()
        if dict_score == 'ori':
            score = 1.0 / len(ori_group)
            dict_score = {k:score for k in ori_group.keys()}
        g, p = np.array([[k, v] for k, v in dict_score.items()]).T
        flag = max(ori_group.keys())
        ## 按照种群分数进行选择交配
        ## 选择交配种群
        cross_group = np.random.choice(g, size = int(len(g)/2), p = p, replace= False)
        for (fa,mo) in itertools.combinations(cross_group, 2):
            flag += 1
            fa_code, mo_code = ori_group[fa], ori_group[mo]
            ## 随机选择切分点
            cut_point = np.random.randint(1, len(fa_code)-1)
            ## 切分基因
            fa_code0, fa_code1 = fa_code[:cut_point], fa_code[cut_point:]
            mo_code0, mo_code1 = mo_code[:cut_point], mo_code[cut_point:]
            ## 基因交换
            new1 = np.hstack([fa_code0, mo_code1])
            ## 变异过程
            prob = np.random.uniform(0, 1)
            if prob < self._change_prob:
                ## 随机挑一个基因点
                change_point = np.random.randint(0, len(new1))
                ## 改变该点的值
                new1[change_point] = not new1[change_point]
            new_dict[flag] = new1
        return new_dict
    
    ## 种群个体能力评价
    def ga_evalue_group(self, group, total_data, evalue_col):
        score_dict = {}
        for g, code in group.items():
            cols = evalue_col[code]
            score = self._objective(total_data.copy(), cols)
            score_dict[g] = score
        return score_dict
    
    def ga_kill_group(self, total_data, ori_group, dict_score, evalue_cols):
        ## 二代目
        sub_group = self.ga_cross_next_group(ori_group, dict_score=dict_score)
        ## 评价
        score_dict = self.ga_evalue_group(sub_group, total_data, evalue_cols)
        score_se = pd.Series(score_dict)
        fact_sco = score_se.sort_values(ascending=False)[:self._sub_num] 
        score_se = score_se.sort_values(ascending=False)[:self._sub_num] / (
            score_se.sort_values(ascending= False)[:self._sub_num].sum())
        liv_group = {i:sub_group[i] for i in score_dict.keys()}
        return liv_group, dict(score_se), dict(fact_sco)
    
    def genetic_run(self, total_data, factors_filed = None, 
                    strong_field = None, weak_field = None):
        
        if factors_filed is not None:
            point = int(np.random.uniform(0, len(factors_filed))/2)
            ori_field = factors_filed[:point]
            add_field = factors_filed[point:]
        elif strong_field is not None and weak_field is not None:
            ori_field = strong_field
            add_field = weak_field
        evalue_cols = np.array(ori_field + add_field)
        #初始种群
        ori_group = {i:self.ga_generate_ori(ori_field, add_field) for i in range(self._group_num)}
        for i in range(self._generations):
            if i == 0:
                sub, sco, fact_sco = self.ga_kill_group(total_data, ori_group, 'ori', evalue_cols)
            else:
                sub, sco, fact_sco = self.ga_kill_group(total_data, sub, sco, evalue_cols)
            now_sco = sco[(list(sco.keys())[0])]
            now_fact_sco = fact_sco[(list(fact_sco.keys())[0])]
            content_str = "generations:{0},i:{1},sco:{2},fact_sco:{3}".format(
                    self._generations, i, now_sco, now_fact_sco)
            print(content_str)
        best_code = pd.Series(sco).sort_values()[-1:].index[0]
        best_field = list(evalue_cols[sub[best_code]])
        return best_field, best_code, sco[best_code]         