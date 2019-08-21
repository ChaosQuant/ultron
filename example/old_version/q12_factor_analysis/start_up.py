import pdb
from factor_analysis import factor_analysis
import time
import datetime
import multiprocessing


def factor_analy(params):
    print(params)
    result = factor_analysis.delay(db_info='postgresql+psycopg2://alpha:alpha@180.166.26.82:8889/alpha',
                           factor_name=params[0], risk_styles=["SIZE"],
                           start_date='2017-01-01', end_date='2018-12-31',
                           universe_name='zz500',benchmark_code=905,
                           freq='10b',session=params[1])
    
session = str(int(time.time() * 1000000 + datetime.datetime.now().microsecond))


grouped_list = []
for i in range(1,3):
    alpha_name = 'alpha_' + str(i)
    grouped_list.append([alpha_name, session])

for params in grouped_list:
    factor_analy(params)
    
'''
cpus = multiprocessing.cpu_count()
with multiprocessing.Pool(processes=cpus) as p:
    alpha_res = p.map(factor_analy, grouped_list)
'''

    
    
