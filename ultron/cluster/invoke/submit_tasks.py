# -*- coding: utf-8 -*-
import six
import base64
import zlib
import time
import datetime
import os
import json
import pdb
from ultron.utilities.redis.redis_client import RedisClient
from ultron.utilities.singleton import Singleton
from ultron.utilities.zlib_engine import zip_compress,unzip_compress
from ultron.utilities.short_uuid import uuid, decode
from ultron.config import config_setting

@six.add_metaclass(Singleton)
class SubmitTask(object):
    def __init__(self, **kwargs):
        if ('host' in kwargs) and ('port' in kwargs) and ('pwd' in kwargs):
            self._redis_client = RedisClient(host=kwargs['host'],
                                          port=kwargs['port'],
                                          password=kwargs['pwd'])
        else:
            self._redis_client = RedisClient(host=config_setting.queue_host,
                                          port=config_setting.queue_port,
                                          password=config_setting.queue_pwd)
    
    def submit_packet(self, uid, packet):
        upload_info = {}
        upload_info['name'] = 'packet'
        upload_info['opcode'] = 'upload_packet'
        upload_info['uid'] = uid
        upload_info['packet_name'] = packet
        file_name = str(decode(uuid())) + '.uldk'
        upload_info['file_name'] = file_name
        task_id = uuid()
        # 压缩
        zip_compress(packet, file_name)
        #上传文件
        with open(os.path.join('./', file_name) ,'rb') as f:
            content = f.read()
            upload_info['file_info'] = base64.b64encode(content).decode()
        #删除打包文件
        if os.path.isfile(file_name):
            os.remove(file_name)
            
        return self._redis_client.hset('ultron:work:update',str(task_id),json.dumps(upload_info))
        
    
submit_task = SubmitTask()