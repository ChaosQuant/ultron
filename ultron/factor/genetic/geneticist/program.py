# -*- coding: utf-8 -*-
import numpy as np
from copy import copy
import pdb
from . operators import crossover_sets,mutation_sets,operators_sets,calc_factor, Function

import warnings
warnings.filterwarnings("ignore")

class Program(object):
    
    def __init__(self, init_depth, method,
                 random_state, factor_sets, 
                 p_point_replace,
                 function_set,
                 operators_set,
                 fitness,
                 coverage_rate=0.5,
                 n_features=0,
                 program=None,
                 parents=None):
        self._init_depth = init_depth
        self._init_method = method
        self._program = program
        self._factor_sets = factor_sets
        self._p_point_replace = p_point_replace
        self._function_set = function_set
        self._operators_set = operators_set
        self._n_features = n_features
        self._fitness = fitness
        self._coverage_rate = coverage_rate
        self._raw_fitness = None # fitness得分
        self._is_valid = True
        self._parents = parents
        if self._program is None:
            self._program = self.build_program(random_state)
    
    def _create_formual(self, apply_formual):
        function = apply_formual[0]
        formula = function.function.__name__
        formula +='('
        for i in range(0,function.arity):
            if i != 0:
                formula += ','
            if apply_formual[i+1] in self._factor_sets:
                formula += '\'' + apply_formual[i+1] + '\''
            else:
                formula += apply_formual[i+1]
        formula += ')'
        return formula
    
    def transform(self):
        if len(self._program) < 2:
            result = 'SecurityCurrentValueHolder(\'' + self._program[0] + '\')'
            print(result)
            return result
        apply_stack = []
        for node in self._program:
            if isinstance(node,Function):
                apply_stack.append([node])
            else:
                apply_stack[-1].append(node)
            while len(apply_stack[-1]) == apply_stack[-1][0].arity + 1:
                result = self._create_formual(apply_stack[-1])
                if len(apply_stack) != 1:
                    apply_stack.pop()
                    apply_stack[-1].append(result)
                else:
                    return result
        
    def export_graphviz(self):
        fade_nodes = None
        terminals = []
        if fade_nodes is None:
            fade_nodes = []
        output = 'digraph program {\nnode [style=filled]\n'
        for i, node in enumerate(self._program):
            fill = '#cecece'
            if isinstance(node,Function):
                if i not in fade_nodes:
                    fill = '#2a5caa'
                terminals.append([node.arity, i])
                output += ('%d [label="%s", fillcolor="%s"] ;\n'
                               % (i, node.function.__name__, fill))
            else:
                if i not in fade_nodes:
                    fill = '#60a6f6'
                if node in self._factor_sets:
                    feature_name = node
                else:
                    feature_name = 'X%s' % node
                output += ('%d [label="%s", fillcolor="%s"] ;\n'
                               % (i, feature_name, fill))
        
                if i == 0 :
                    output += '}'
                    return output
                terminals[-1][0] -= 1
                terminals[-1].append(i)
                while terminals[-1][0] == 0:
                    output += '%d -> %d ;\n' % (terminals[-1][1],
                                                terminals[-1][-1])
                    terminals[-1].pop()
                    if len(terminals[-1]) == 2:
                        parent = terminals[-1][-1]
                        terminals.pop()
                        if not terminals:
                            output += '}'
                            return output
                        terminals[-1].append(parent)
                        terminals[-1][0] -= 1
                    
    def build_program(self, random_state):
        #在范围内选取树形深度
        if self._init_method == 'half and half':
            method = ('full' if random_state.randint(2) else 'grow')
        else:
            method = self._init_method
        if isinstance(self._init_depth, int):
            max_depth = self._init_depth
        else:
            max_depth = random_state.randint(*self._init_depth)
        function = random_state.randint(len(self._operators_set))
        function = self._operators_set[function]
        program = [function]
        terminal_stack = [function.arity]
        while terminal_stack:
            depth = len(terminal_stack)
            choice = self._n_features + len(self._operators_set)
            choice = np.random.randint(0,choice)
            if depth < max_depth and (method == 'full' or
                                        choice <= len(self._operators_set)):
                function = self._operators_set[np.random.randint(0,len(self._operators_set)-1)] 
                program.append(function)
                terminal_stack.append(function.arity)
            else:
                factor = self._factor_sets[np.random.randint(0,len(self._factor_sets)-1)]
                program.append(factor)
                terminal_stack[-1] -= 1
                while terminal_stack[-1] == 0:
                    terminal_stack.pop()
                    if not terminal_stack:
                        return program
                    terminal_stack[-1] -= 1
        return program
    
    def get_subtree(self, random_state, program=None):
        if program is None:
            program = self._program
        # Choice of crossover points follows Koza's (1992) widely used approach
        # of choosing functions 90% of the time and leaves 10% of the time.
        probs = np.array([0.9 if node in self._operators_set else 0.1 for node in program])
        probs = np.cumsum(probs / probs.sum())
        start = np.searchsorted(probs, random_state.uniform())
        stack = 1
        end = start
        while stack > end - start:
            node = program[end]
            if node in self._operators_set:
                stack += node.arity
            end += 1
        return start, end

    ##复制
    def reproduce(self):
        return copy(self._program)
    
    ##交叉
    def crossover(self, donor, random_state):
        start, end = self.get_subtree(random_state)
        end -= 1
        removed = range(start, end)
        donor_start, donor_end = self.get_subtree(random_state, donor)
        donor_removed = list(set(range(len(donor))) -
                             set(range(donor_start, donor_end)))
        return (self._program[:start] +
                donor[donor_start:donor_end] +
                self._program[end:]), removed, donor_removed
    ##树变异        
    def subtree_mutation(self, random_state):
        chicken = self.build_program(random_state)
        return self.crossover(chicken, random_state)
    
    ##突变异
    def hoist_mutation(self, random_state):
        start, end = self.get_subtree(random_state)
        subtree = self._program[start:end]
        sub_start, sub_end = self.get_subtree(random_state, subtree)
        hoist = subtree[sub_start:sub_end]
        removed = list(set(range(start, end)) -
                       set(range(start + sub_start, start + sub_end)))
        return self._program[:start] + hoist + self._program[end:],removed
    
    ##点变异
    def point_mutation(self, random_state):
        program = copy(self._program)
        mutate = np.where(random_state.uniform(size=len(program)) <
                          self._p_point_replace)[0]
        
        for node in mutate:
            if program[node] in self._operators_set:
                activy = program[node].arity
                #找到参数个数替换
                if activy == 1:
                    replace_node = mutation_sets[np.random.randint(0,len(mutation_sets)-1)]
                else:
                    replace_node = crossover_sets[np.random.randint(0,len(crossover_sets)-1)]
                program[node] = replace_node
            else:
                factor = self._factor_sets[np.random.randint(0,len(self._factor_sets)-1)]
                program[node] = factor
        return program, list(mutate)
    
    def raw_fitness(self, total_data, factor_sets, default_value, indexs=['trade_date'], key='code'):
        #计算因子值
        try:
            expression = self.transform()
            if expression is None:
                self._raw_fitness = default_value
                self._is_valid = False
            else:
                factor_data = calc_factor(expression, total_data, indexs, key)
                factor_data = factor_data.replace([np.inf, -np.inf], np.nan)
                ##检测覆盖率
                coverage_rate  =  1 - factor_data['transformed'].isna().sum() / len(factor_data['transformed'])
                if coverage_rate < self._coverage_rate:
                    self._raw_fitness = default_value
                    self._is_valid = False
                else:
                    raw_fitness = self._fitness(factor_data, total_data, factor_sets)
                    self._raw_fitness = default_value if np.isnan(raw_fitness) else raw_fitness
        except Exception as e:
            print(e)
            self._raw_fitness = default_value
            self._is_valid = False