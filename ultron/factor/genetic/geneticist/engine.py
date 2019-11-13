# -*- coding: utf-8 -*-

import numpy as np
import pdb,time,datetime,pickle,itertools,os
from ultron.factor.genetic.geneticist.genetic import Gentic
from . operators import operators_sets
from .... utilities.mlog import MLog

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min

class Engine(object):
    def __init__(self, population_size=2000,
                generations=MAX_INT,tournament_size=20,
                stopping_criteria=0.0, factor_sets=None,
                init_depth=(5, 6),init_method='full',
                operators_set=operators_sets,
                n_jobs=1,
                p_crossover=0.9,
                p_subtree_mutation=0.01,
                p_hoist_mutation=0.01,
                p_point_mutation=0.01,
                p_point_replace=0.05,
                greater_is_better=True,#True 倒序， False 正序
                verbose=1,
                is_save=1,
                rootid=0,
                session=0,
                standard_score=2,# None代表 根据tournament_size保留种群  standard_score保留种群
                out_dir='result',
                backup_cycle = 0,# 后备数据周期，主要用于在时间序列上的问题
                convergence = None, # 收敛值，若为None，则不需要收敛值。
                low_memory = False,
                fitness=None,
                random_state=None,
                custom_params = None,
                save_model=None):
        MLog().config(name='Gentic')
        self._population_size = population_size
        self._generations = MAX_INT if generations == 0 else generations
        self._tournament_size = tournament_size
        self._stopping_criteria = stopping_criteria
        self._factor_sets = factor_sets
        self._init_depth = init_depth
        self._init_method = init_method
        self._operators_set = operators_set
        self._function_set = [op.name for op in self._operators_set]
        self._p_crossover = p_crossover
        self._p_subtree_mutation = p_subtree_mutation
        self._p_hoist_mutation = p_hoist_mutation
        self._p_point_mutation = p_point_mutation
        self._p_point_replace = p_point_replace
        self._random_state = random_state
        self._greater_is_better = greater_is_better
        self._standard_score = standard_score
        self._fitness = fitness
        self._n_jobs = n_jobs
        self._backup_cycle = backup_cycle
        self._custom_params = custom_params
        self._low_memory = low_memory
        self._verbose = verbose
        self._is_save = is_save
        self._out_dir = out_dir
        self._convergence = convergence
        self._rootid = int(time.time() * 1000000 + datetime.datetime.now().microsecond) if rootid == 0 else rootid
        self._session = int(time.time() * 1000000 + datetime.datetime.now().microsecond) if session == 0 else session
        self._save_model = self.save_model if save_model is None else save_model
        
        
    def run_gentic(self, total_data):
        gentic = Gentic(population_size=self._population_size,
                generations=self._generations,tournament_size=self._tournament_size,
                stopping_criteria=self._stopping_criteria, factor_sets=self._factor_sets,
                init_depth=self._init_depth,init_method=self._init_method,
                operators_set=self._operators_set,
                n_jobs=self._n_jobs,p_crossover=self._p_crossover,
                p_subtree_mutation=self._p_subtree_mutation,
                p_hoist_mutation=self._p_hoist_mutation,
                p_point_mutation=self._p_point_mutation,
                p_point_replace=self._p_point_replace,
                greater_is_better=self._greater_is_better,
                verbose=self._verbose,
                is_save=self._is_save,
                rootid=self._rootid,
                standard_score=self._standard_score,# None代表 根据tournament_size保留种群  standard_score保留种群
                out_dir=self._out_dir,
                backup_cycle = self._backup_cycle,# 后备数据周期，主要用于在时间序列上的问题
                convergence = self._convergence, # 收敛值，若为None，则不需要收敛值。
                low_memory = self._low_memory,
                fitness=self._fitness,
                session = self._session,
                random_state=self._random_state,
                custom_params = self._custom_params,
                save_model=self._save_model)
        
        gentic.train(total_data=total_data)
        result = gentic._run_details
        raw_fitness = result['best_fitness'][-1]
        del gentic
        return raw_fitness
    
    def train(self, total_data):
        raw_fitness = 0 
        while raw_fitness < self._stopping_criteria:
            raw_fitness = self.run_gentic(total_data)
            pdb.set_trace()