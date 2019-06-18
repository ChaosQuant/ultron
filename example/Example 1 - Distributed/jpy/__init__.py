import sys
sys.path.append('../..')
from ultron.cluster.invoke.app_engine import create_app

app = create_app('distributed',['jpy.task1','jpy.task2'])
