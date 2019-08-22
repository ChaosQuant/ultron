import sys
sys.path.append('../../..')
from ultron.cluster.invoke.app_engine import create_app

app = create_app('factor_analysis',['jpy.task1','jpy.task2'])
