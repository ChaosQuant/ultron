import sys
#sys.path.append('../../../../ultron')
from ultron.cluster.invoke.app_engine import create_app

app = create_app('distributed',['factors.analysis'])
