# -*- coding: utf-8 -*-
import six
import base64
import zlib
import time
import datetime
import os
import json
from ultron.utilities.redis.redis_client import RedisClient
from ultron.utilities.singleton import Singleton
import ultron.config as config

@six.add_metaclass(Singleton)
class SubmitTask(object):
    def __init__(self, **kwargs):
        if ('host' in kwargs) and ('port' in kwargs) and ('pwd' in kwargs):
            self._redis_client = RedisClient(host=kwargs['host'],
                                          port=kwargs['port'],
                                          password=kwargs['pwd'])
        else:
            self._redis_client = RedisClient(host=config.redis_host,
                                          port=config.redis_port,
                                          password=config.redis_pwd)
        
    def submit_packet(self, uid, dir_name, file_list):
        upload_info = {}
        upload_info['name'] = 'packet'
        upload_info['opcode'] = 'upload_packet'
        upload_info['uid'] = uid
        upload_info['dir_name'] = dir_name
        task_id = int(time.time() * 1000000 + datetime.datetime.now().microsecond)
        file_info = []
        for file_name in file_list:
            with open(os.path.join(dir_name, file_name) ,'r') as f:
                content = bytes(f.read(), encoding = "utf8")
                file_info.append({'file_name':file_name, 
                              'content': str(base64.b64encode(zlib.compress(content)),encoding = "utf-8") })
        upload_info['file_info'] = file_info
        return self._redis_client.hset('ultron:work:update',str(task_id),json.dumps(upload_info))

submit_task = SubmitTask()