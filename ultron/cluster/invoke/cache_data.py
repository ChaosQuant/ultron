# -*- coding: utf-8 -*-
import six
from ultron.utilities.singleton import Singleton
from ultron.utilities.redis.redis_client import RedisClient
import ultron.proto.cache_data_pb2
from ultron.config import config_setting
import zlib
import base64
import pdb

@six.add_metaclass(Singleton)
class CacheData(object):
    def __init__(self, **kwargs):
        if ('host'  in kwargs) and ('port'  in kwargs) and ('pwd'  in kwargs):
            self._host = kwargs['host']
            self._port = kwargs['port']
            self._port = kwargs['pwd']
        else:
            self._host = config_setting.queue_host
            self._port = config_setting.queue_port
            self._pwd = config_setting.queue_pwd
        self._queue = 'ultron:cache'
        self._zip_level = 9
        #创建redis连接
        self._redis_client = RedisClient(host=self._host,
                                          port=self._port,
                                          password=self._pwd, db=6)
        
    def set_cache(self, session, key, values):
        cache_data_pb = ultron.proto.cache_data_pb2.CacheData()
        cache_data_pb.session = str(session).encode('raw_unicode_escape')
        cache_data_pb.key = str(key).encode('raw_unicode_escape')
        cache_data_pb.data_stream = zlib.compress(bytes(values,encoding='utf8'), self._zip_level)
        self._redis_client.hset(self._queue, str(key) + str(session), 
                                base64.b64encode(cache_data_pb.SerializeToString()))
    
    def get_cache(self, session, key, is_del=True):
        base64_values_str = self._redis_client.hget(self._queue, str(key) + str(session))
        if is_del:
            self._redis_client.hdel(self._queue, str(key) + str(session))
        zlilb_values = base64.b64decode(base64_values_str)
        cache_data_pb = ultron.proto.cache_data_pb2.CacheData()
        cache_data_pb.ParseFromString(zlilb_values)
        values = zlib.decompress(cache_data_pb.data_stream)
        return values
    
cache_data = CacheData()