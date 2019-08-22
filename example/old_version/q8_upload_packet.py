# -*- coding: utf-8 -*-
import json
import datetime
import time
import os
import zlib
import base64
import sys
import pdb
sys.path.append('..')
from ultron.utilities.redis.redis_client import RedisClient

def upload(redis_client, dir_name, file_list):
    upload_info = {}
    upload_info['name'] = 'packet'
    upload_info['opcode'] = 'upload_packet'
    upload_info['uid'] = 1000
    upload_info['dir_name'] = dir_name
    task_id = int(time.time() * 1000000 + datetime.datetime.now().microsecond)
    file_info = []
    for file_name in file_list:
        with open(os.path.join(dir_name, file_name) ,'r') as f:
            content = bytes(f.read(), encoding = "utf8")
            file_info.append({'file_name':file_name, 
                              'content': str(base64.b64encode(zlib.compress(content)),encoding = "utf-8") })
    upload_info['file_info'] = file_info
    pdb.set_trace()
    redis_client.hset('ultron:work:update',str(task_id),json.dumps(upload_info))

from ultron.utilities.redis.redis_client import RedisClient
redis_client = RedisClient(host='47.95.193.202',port=6378,password='12345678dx')

upload(redis_client, 'q7_task',['polymeriza.py','tasks.py'])
