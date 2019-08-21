# -*- coding: utf-8 -*-
import sys
import json
import datetime
import time
sys.path.append('..')


from ultron.utilities.redis.redis_client import RedisClient
redis_client = RedisClient(host='47.95.193.202',port=6378,password='12345678dx')

task_id = time.time() * 1000000 + datetime.datetime.now().microsecond

task_info = {'name':'tasks','opcode':'shutoff_task','work_name':'polymeriza','dir_name':'./q7_task'}

redis_client.hset('ultron:work:ctask',str(task_id),json.dumps(task_info))
