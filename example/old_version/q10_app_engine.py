# -*- coding: utf-8 -*-
import sys
import pdb
sys.path.append('..')
from ultron.cluster.invoke.app_engine import create_app

app = create_app('q10_app_engine')

@app.task
def send_mail(email):
    print('sending email %s' %(email))
    import time
    return "success"