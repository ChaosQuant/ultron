import time
import numpy as np
from jpy import app
import multiprocessing

def sub_calc(params):
    x = params[0]
    y = params[1]
    i = params[2]
    ret = x + i + y + 2 * i
    return ret

@app.task(ignore_result=True)
def add(x, y):
    params_list = []
    cpus = multiprocessing.cpu_count()
    for i in range(1,100):
        params_list.append([x, y, i])
    with multiprocessing.Pool(processes=cpus) as p:
        res = p.map(sub_calc, params_list)
    return np.array(res).mean()
    
    