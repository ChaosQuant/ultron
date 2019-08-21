# -*- coding: utf-8 -*-
import sys
import pdb
sys.path.append('..')
from ultron.cluster.invoke.submit_tasks import submit_task


submit_task.submit_packet('DK', 'q7_task',['polymeriza.py','tasks.py'])