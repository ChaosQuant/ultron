import pdb
import sys
import datetime
from celery import Celery
#from ultron.factor.engine.polymeriza import Polymerization

app = Celery(__file__.split('.')[0], broker='redis://:12345678dx@47.95.193.202:6378/0')

@app.task
def polymeriza_factor(factors_setting, common_setting):
    trade_date_list = [datetime.date(2018, 12, 7), datetime.date(2018, 6, 15), datetime.date(2018, 11, 30), datetime.date(2018, 6, 29), datetime.date(2018, 8, 3), datetime.date(2018, 9, 14), datetime.date(2018, 10, 12), datetime.date(2018, 7, 13), datetime.date(2018, 9, 21), datetime.date(2018, 6, 8), datetime.date(2018, 8, 17), datetime.date(2018, 6, 22), datetime.date(2018, 6, 1), datetime.date(2018, 9, 7), datetime.date(2018, 10, 26), datetime.date(2018, 11, 16), datetime.date(2018, 8, 31), datetime.date(2018, 7, 27), datetime.date(2018, 7, 20), datetime.date(2018, 9, 28), datetime.date(2018, 11, 9), datetime.date(2018, 7, 6), datetime.date(2018, 12, 14), datetime.date(2018, 8, 24), datetime.date(2018, 12, 28), datetime.date(2018, 10, 19), datetime.date(2018, 11, 2), datetime.date(2018, 11, 23), datetime.date(2018, 8, 10), datetime.date(2018, 12, 21)]
    
    #polyerization = Polymerization(common_setting, factors_setting)
    #print(polyerization.on_work_by_interval(trade_date_list))
