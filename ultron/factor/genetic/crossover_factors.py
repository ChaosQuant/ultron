# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import gevent.monkey
import multiprocessing
import itertools,time,pdb
from . accumulators import mutated_pool,cross_pool,dependency,calc_new_factor
GLOBAL_ORDER_ID = 0

class GeneticCrossFactors(object):
    def __init__(self, del_prob, add_prob, cross_prob,
                 change_prob, conver_prob, cross_rate=0.01,
                 change_rate=0.01, generation=500, group_num=10,
                 parallel = None,objective=None):
        #ori:原始特征，主要用于计算时候获取原始因子  new:变异特征   
        self._del_prob = del_prob # 删除原始特征概率
        self._add_prob = add_prob # 添加新特征概率
        self._cross_prob =  cross_prob #交叉概率
        self._change_prob =  change_prob #变异概率
        self._conver_prob = conver_prob # 收敛差值
        self._cross_rate = cross_rate # 交叉比例
        self._change_rate = change_rate # 变异比例
        self._generations = generation
        self._group_num = group_num
        self._objective = objective
        self._parallel = parallel if parallel is not None else multiprocessing.cpu_count()
        

        
    # 初代种群生成
    def ga_generate_ori(self, ori_field, add_field, evalue_cols):
        ## 选取原始特征过程
        ori_list = (np.random.uniform(0, 1, (1, len(ori_field))) > self._del_prob).tolist()[0]
        add_list = (np.random.uniform(0, 1, (1, len(add_field))) < self._add_prob).tolist()[0]
        new_list = ori_list + add_list
        new_list = [1 if i> 0 else 0 for i in new_list]
        new_array = evalue_cols[np.array([True if i > 0 else False for i in new_list])]
        #return {'ori':new_array, 'new':new_array}
        return new_array
    
   ## 交叉变异过程
    def ga_cross_next_group(self, ori_group, ori_columns, dict_score = 'ori', generation=0):
        new_dict = ori_group.copy()
        if generation == 0:
            score = 1.0 / len(ori_group)
            dict_score = {k:score for k in ori_group.keys()}
        g, p = np.array([[k, v] for k, v in dict_score.items()]).T
        cross_group = np.random.choice(g, size = int(len(g)/2), p = p, replace= False)
        for (fa,mo) in itertools.combinations(cross_group, 2):
            global GLOBAL_ORDER_ID
            GLOBAL_ORDER_ID += 1
            flag = GLOBAL_ORDER_ID
            fa_code, mo_code = ori_group[fa], ori_group[mo]
            cut_point = np.random.randint(1, len(fa_code)/2)
            fa_code0, fa_code1 = fa_code[:cut_point], fa_code[cut_point:]
            mo_code0, mo_code1 = mo_code[:cut_point], mo_code[cut_point:]
            new1 = np.hstack([fa_code0, mo_code1])#前一半父类基因，后一半母类基因
            #父类母类中存在共用基因，只保留一个基因
            new1 = np.array(list(set(new1)))
            
            #加入原始基因增加遗传多样性
            ori_prob = np.random.uniform(0, 1)
            if ori_prob < 0.2:
                section_columns = set(ori_columns) - set(new1)
                new_code = np.array(list(section_columns))[np.random.randint(0, len(section_columns), 
                                                                             int(len(section_columns) * 0.01 + 1))]
                pos = np.random.randint(0, len(new1), len(new_code))
                new1[pos] = new_code #前一半父类基因，后一半母类基因, 最后一半加入原始基因  
            
            new_group = list(new1.copy())
            #count = int(len(new_group) * self._cross_prob)
            #交叉
            prob = np.random.uniform(0, 1)
            if prob < self._cross_prob:
                count = int(len(new_group) * self._cross_rate + 1)
                for i in range(0, count):
                    fa_pos = np.random.randint(0, len(new1)/2) # 取为1
                    mo_pos = np.random.randint(len(new1)/2, len(new1)) # 取为1
                    accumulators = cross_pool[int(np.random.uniform(1, len(cross_pool) - 1))]
                    #判断是否为原始
                    if new1[fa_pos] in ori_columns and new1[mo_pos] in ori_columns:
                        new_factor = accumulators.__name__ + '(\'' + new1[fa_pos] + '\',\'' + new1[mo_pos] + '\')'
                    elif new1[fa_pos] in ori_columns and new1[mo_pos] not in ori_columns:
                        new_factor = accumulators.__name__ + '(\'' + new1[fa_pos] + '\',' + new1[mo_pos] + ')'
                    elif new1[fa_pos] not in ori_columns and new1[mo_pos] in ori_columns:
                        new_factor = accumulators.__name__ + '(' + new1[fa_pos] + ',\'' + new1[mo_pos] + '\')'
                    elif new1[fa_pos] not in ori_columns and new1[mo_pos] not in ori_columns:
                        new_factor = accumulators.__name__ + '(' + new1[fa_pos] + ',' + new1[mo_pos] + ')'
                    new_group.append(new_factor)
            #变异    
            prob = np.random.uniform(0, 1)
            if prob < self._change_prob:
                count = int(len(new_group) * self._change_rate + 1)
                for i in range(0, count):
                    pos = np.random.randint(0, len(new1))#交叉生成的不变异
                    accumulators = mutated_pool[int(np.random.uniform(2, len(mutated_pool) -1))]
                    #判断是否为原始
                    if new1[pos] in ori_columns:
                        new_factor = accumulators.__name__ + '(\'' + new1[pos] + '\')'
                    else:
                        new_factor = accumulators.__name__ + '(' + new1[pos] + ')'
                    new_group[pos] = new_factor
            new_dict[flag] = np.array(new_group)
        return new_dict
    
    #种群特征计算
    def calc_evalue_group(self, params):
        sub_group, evalue_cols, total_data, diff_filed, g =  params
        #sub_factor_data = total_data.set_index(['trade_date','code'])[sub_group['ori']].T
        #自身变异算法使用apply计算
        mutated_cross_columns = set(sub_group) - set(total_data.columns) #交叉变异列
        if len(mutated_cross_columns) > 0:
            result = dependency(mutated_cross_columns)
            factor_columns = ','.join(result.values()).split(',')
            sub_factor_data = total_data.set_index(['trade_date'])[factor_columns + ['code']]
            news_factor_data = calc_new_factor(mutated_cross_columns, sub_factor_data)
            surplus = set(sub_group) - mutated_cross_columns
            #复制剩余无需更改的
            for ori in list(surplus):
                news_factor_data[ori] = total_data[ori].values
        else:
            news_factor_data = total_data[list(sub_group)].copy()
        #复制其他项目
        for diff in diff_filed:
            news_factor_data[diff] = total_data[diff].values
        score = self._objective(news_factor_data.replace([np.inf, -np.inf], np.nan), sub_group)
        if score == np.nan: score = 0
        return score, sub_group, g
        
        
    ## 种群个体能力评价
    def ga_evalue_group(self, sub_group, total_data, evalue_cols, diff_filed):
        jobs = []
        score_dict = {}
        cols_dict = {}
        start_time = time.time()
        '''
        for key in sub_group.keys():
            #切换多进程计算
            score, new_group, g = self.calc_evalue_group([sub_group[key], evalue_cols, total_data, 
                                     diff_filed,key])
            score_dict[g] = score
            cols_dict[g] = new_group
        '''
        cpus_count = multiprocessing.cpu_count() if multiprocessing.cpu_count() < len(sub_group) else len(sub_group)
        for key in sub_group.keys():
            jobs.append([sub_group[key], evalue_cols, total_data, diff_filed,key])
        with multiprocessing.Pool(processes=cpus_count) as p:
            values_list = p.map(self.calc_evalue_group, jobs)
        for values in values_list:
            score =  values[0]
            sub_group = values[1]
            g = values[2]
            score_dict[g] = score
            cols_dict[g] = sub_group
        print(time.time() - start_time)
        return score_dict, cols_dict
        
        
    #种群变异
    def ga_kill_group(self, total_data, ori_group, dict_score, evalue_cols, diff_filed, generation = 0):        
        # 生成新一代特征
        ori_columns = list(set(total_data.columns) - set(diff_filed))
        sub_group = self.ga_cross_next_group(ori_group, ori_columns, dict_score=dict_score,generation=generation)
        ori_score_dict, cols_dict = self.ga_evalue_group(sub_group, total_data, evalue_cols, diff_filed)
        ori_score_se = pd.Series(ori_score_dict)
        print('种群数%d, 种群均分:%f'%(len(ori_score_se),ori_score_se.mean()))
        #真实分数
        fact_se = ori_score_se.sort_values(ascending=False)[:self._group_num] 
        #比例分数
        score_se = ori_score_se.sort_values(ascending=False)[:self._group_num] / (
            ori_score_se.sort_values(ascending= False)[:self._group_num].sum())
        liv_group = {}
        for k in score_se.keys():
            liv_group[k] = cols_dict[k]
        return score_se, dict(fact_se), liv_group
            
    def genetic_run(self, total_data, diff_filed, sequence=['trade_date','code'],
                    factors_filed = None, strong_field = None, 
                    weak_field = None, is_best=True):
        if factors_filed is not None:
            point = int(np.random.uniform(0, len(factors_filed))/2)
            ori_field = factors_filed[:point]
            add_field = factors_filed[point:]
        elif strong_field is not None and weak_field is not None:
            ori_field = strong_field
            add_field = weak_field
        
        total_data = total_data.sort_values(by=sequence,ascending=True)
        evalue_cols = np.array(ori_field + add_field)
        last_score = 0.0
        #初始种群
        ori_group = {i:self.ga_generate_ori(ori_field, add_field, evalue_cols) for i in range(self._group_num)}
        global GLOBAL_ORDER_ID
        GLOBAL_ORDER_ID += (len(ori_group) - 1)
        for i in range(self._generations):
            if i == 0:
                score_se, fact_se, liv_group  = self.ga_kill_group(
                    total_data, ori_group, 'ori', evalue_cols, diff_filed, 0)
            else:
                score_se, fact_se, liv_group  = self.ga_kill_group(
                    total_data, liv_group, score_se, evalue_cols, diff_filed, 0)
                
            best_fact_score = pd.Series(fact_se).sort_values(ascending=False)[0:1]
            best_score = pd.Series(score_se).sort_values(ascending=False)
            diff_fact_score = best_fact_score.values[0] - last_score
            diff_score = best_score[0:1].values[0] - best_score[-1:].values[0]
            
            now_best_score = (best_fact_score.values[0] if best_fact_score.values[0] > last_score else last_score)
            print('繁衍代数:%d,最好分数:%f,%d(%f)和%d(%f)最好组分数差值%f,%d代最好最差种群分数差值%f'%((i+1),
               now_best_score,
               i+1,
               best_fact_score.values[0], 
               i, last_score, 
               diff_fact_score,i+1,diff_score)) 
            best_code = list(liv_group.keys())[0]
            best_group = liv_group[best_code]
            if diff_fact_score < self._conver_prob and diff_score < self._conver_prob:
                break
            last_score = best_fact_score.values[0]
            
        if is_best:
            best_code = pd.Series(fact_se).sort_values(ascending=False)[0:1].index[0]
            best_list = liv_group[best_code]
            best_field = cols[[True if i> 0 else False for i in best_list]]
            return best_code, best_field
        else:
            field_group = {}
            for k, g in liv_group.items():
                field_group[k] = cols[[True if i> 0 else False for i in g]]
            return field_group