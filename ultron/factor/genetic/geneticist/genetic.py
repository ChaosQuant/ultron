# -*- coding: utf-8 -*-

import numpy as np
import pdb,time
import itertools
from joblib import Parallel, delayed
from copy import copy
from . program import Program
from . operators import operators_sets
from .... utilities.jobs import partition_estimators
from .... utilities.utils import check_random_state

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min


def parallel_evolve(n_programs, parents, total_data, seeds, greater_is_better, params):
    tournament_size = params['tournament_size']
    function_set = params['function_set']
    operators_set = params['operators_set']
    init_depth = params['init_depth']
    init_method = params['init_method']
    method_probs = params['method_probs']
    p_point_replace = params['p_point_replace']
    factor_sets = params['factor_sets']
    fitness = params['fitness']
    def _tournament(tour_parents):
        contenders = random_state.randint(0, len(tour_parents), tournament_size)
        raw_fitness = [tour_parents[p]._raw_fitness for p in contenders]
        if greater_is_better:
            parent_index = contenders[np.argmax(raw_fitness)]
        else:
            parent_index = contenders[np.argmin(raw_fitness)]
        return tour_parents[parent_index], parent_index
    
    programs = []
    for i in range(n_programs):
        random_state = check_random_state(seeds[i])
        if parents is None:
            program = None
            genome = None
        else:
            method = random_state.uniform()
            parent, parent_index = _tournament(copy(parents))
            if method < method_probs[0]: # crossover
                donor, donor_index = _tournament(copy(parents))
                program, removed, remains = parent.crossover(donor._program, random_state)
                genome = {'method':'Crossover',
                         'parent_idx':parent_index,
                         'parent_nodes':removed,
                         'donor_idx':donor_index,
                         'donor_nodes':remains}
            elif method < method_probs[1]: #  subtree_mutation
                program, removed, _ = parent.subtree_mutation(random_state)
                genome = {'method': 'Subtree Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < method_probs[2]: # hoist_mutation
                program, removed = parent.hoist_mutation(random_state)
                genome = {'method': 'Hoist Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < method_probs[3]: # point_mutation
                program,mutated = parent.point_mutation(random_state)
                genome = {'method': 'Point Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': mutated}
            else:
                program = parent.reproduce() # reproduction
                genome = {'method': 'Reproduction',
                          'parent_idx': parent_index,
                          'parent_nodes': []}
        
        program = Program(init_depth=init_depth, method=init_method, random_state=random_state,
                          factor_sets=factor_sets, function_set=function_set,
                          operators_set = operators_set,
                          p_point_replace=p_point_replace, fitness=params['fitness'],
                          n_features=2, program=program, parents=genome)
        
        default_value = MIN_INT if greater_is_better else MAX_INT
        program.raw_fitness(total_data, factor_sets, default_value=default_value)
        
        programs.append(program)
    return programs
        
class Gentic(object):
    def __init__(self, population_size=2000,
                generations=20,tournament_size=20,
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
                low_memory = False,
                fitness=None,
                random_state=None):
        self._population_size = population_size
        self._generations = generations
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
        self._fitness = fitness
        self._n_jobs = n_jobs
        self._low_memory = low_memory
        self._verbose = verbose
     
        
    def train(self, total_data):
        random_state = check_random_state(self._random_state)
        self._method_probs = np.array([self._p_crossover,
                                       self._p_subtree_mutation,
                                       self._p_hoist_mutation,
                                       self._p_point_mutation])
        
        self._method_probs = np.cumsum(self._method_probs)
        
        if self._method_probs[-1] > 1:
            raise ValueError('The sum of p_crossover, p_subtree_mutation, '
                             'p_hoist_mutation and p_point_mutation should '
                             'total to 1.0 or less.')
        
        if self._init_method not in ('half and half', 'grow', 'full'):
            raise ValueError('Valid program initializations methods include '
                             '"grow", "full" and "half and half". Given %s.'
                             % self.init_method)
            
        if (isinstance(self._init_depth, tuple) and len(self._init_depth) != 2):
            raise ValueError('init_depth should be a tuple with length two.')
        
        if (isinstance(self._init_depth, tuple) and (self._init_depth[0] > self._init_depth[1])):
            raise ValueError('init_depth should be in increasing numerical '
                             'order: (min_depth, max_depth).')
        
        params = {}
        params['tournament_size'] = self._tournament_size
        params['function_set'] = self._function_set
        params['operators_set'] = self._operators_set
        params['init_depth'] = self._init_depth
        params['init_method'] = self._init_method
        params['method_probs'] = self._method_probs
        params['p_point_replace'] = self._p_point_replace
        params['factor_sets'] = self._factor_sets
        params['fitness'] = self._fitness 
    
        self._programs = []
        self._best_programs = None
        self._run_details = {'generation': [],
                             'average_fitness': [],
                             'best_fitness': [],
                             'generation_time': [],
                             'best_programs':[]}
        
        
        prior_generations = len(self._programs)
        n_more_generations = self._generations - prior_generations
        for gen in range(prior_generations, self._generations):
            start_time = time.time()
            if gen == 0:
                parents = None
            else:
                parents = self._programs[gen - 1]
                
            n_jobs, n_programs, starts = partition_estimators(
                self._population_size, self._n_jobs)
            
            seeds = random_state.randint(MAX_INT, size=self._population_size)
            population = Parallel(n_jobs=n_jobs,
                                  verbose=self._verbose)(
                delayed(parallel_evolve)(n_programs[i], parents, total_data, seeds, self._greater_is_better, params)
                for i in range(n_jobs))
            
            population = list(itertools.chain.from_iterable(population))
            fitness = [program._raw_fitness for program in population]
            
            self._programs.append(population)
            
            if not self._low_memory:
                for old_gen in np.arange(gen, 0, -1):
                    indices = []
                    for program in self._programs[old_gen]:
                        if program is not None:
                            if 'parent_idx' in program._parents:
                                indices.append(program._parents['parent_idx'])
                    indices = set(indices)
                    for idx in range(self._population_size):
                        if idx not in indices:
                            self._programs[old_gen - 1][idx] = None 
            elif gen > 0:
                self._programs[gen - 1] = None
            
            
            if self._greater_is_better:
                best_programs = np.array(population)[np.argsort(fitness)[-self._tournament_size:]]
            else:
                best_programs = np.array(population)[np.argsort(fitness)[:self._tournament_size]]
            
            if self._best_programs is not None:
                current_programs = np.concatenate([best_programs,self._best_programs])
                identification_dict = {}
                for program in current_programs:
                    identification_dict[program._identification] = program
                current_programs = list(identification_dict.values())
                current_fitness = [program._raw_fitness for program in current_programs]
                if self._greater_is_better:
                    best_programs = np.array(current_programs)[np.argsort(current_fitness)[-self._tournament_size:]]
                else:
                    best_programs = np.array(current_programs)[np.argsort(current_fitness)[:self._tournament_size]]
            else:
                identification_dict = {}
                for program in best_programs:
                    identification_dict[program._identification] = program
                best_programs = list(identification_dict.values())
            self._best_programs = best_programs
            
            self._run_details['generation'].append(gen)
            self._run_details['average_fitness'].append(np.mean(fitness))
            self._run_details['best_fitness'].append(self._best_programs[0]._raw_fitness)
            generation_time = time.time() - start_time
            self._run_details['generation_time'].append(generation_time)
            self._run_details['best_programs'].append(self._best_programs)
            print([program._raw_fitness for program in self._best_programs])
            
            if self._greater_is_better:
                best_fitness = fitness[np.argmax(fitness)]
                if best_fitness >= self._stopping_criteria:
                    break
            else:
                best_fitness = fitness[np.argmin(fitness)]
                if best_fitness <= self._stopping_criteria:
                    break            