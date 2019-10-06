# -*- coding: utf-8 -*-
import pickle,itertools,sys,pdb
from ultron.factor.genetic.genetic_factors.program import Program
from ultron.utilities.utils import check_random_state

pdb.set_trace()
with open('factor_data.pkl','rb') as file2:
    total_data = pickle.load(file2)
    
factor_sets = [i for i in list(set(total_data.columns)) if i not in ['trade_date','code','ret']]
random_state = check_random_state(None)
program = Program(init_depth=5, method='nt', random_state=random_state, factor_sets=factor_sets,
                 n_features=2)
print('----')