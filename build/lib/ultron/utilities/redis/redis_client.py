# -*- coding: utf-8 -*-
import json
import logging
import sys

import gevent
import time

from redis.client import pairs_to_dict
# from rediscluster import StrictRedisCluster
from redis import Redis, ConnectionPool, ResponseError, ConnectionError, TimeoutError

log = logging.getLogger(__name__)

class SingleRedisClient(Redis):

    def __init__(self, *args, **kwargs):
        self.status = type('RedisStatus', (), {'alive_timestamp': 0})
        startup_nodes = kwargs.get('startup_nodes')
        if startup_nodes:
            host = startup_nodes[0].get('host')
            password = startup_nodes[0].get('password')
            if 'redis://' not in host:
                kwargs['host'] = host
                kwargs['port'] = startup_nodes[0].get('port')
                if sys.version > '3':
                    kwargs.pop('startup_nodes')
                else:
                    del kwargs['startup_nodes']
                kwargs['password'] = password
            else:
                url = host.format(password=password)
                connection_pool = ConnectionPool.from_url(url, db=0, **kwargs)
                kwargs['connection_pool'] = connection_pool
                if sys.version > '3':
                    kwargs.pop('startup_nodes')
                else:
                    del kwargs['startup_nodes']
        else:
            host = kwargs.get('host')
            port = kwargs.get('port')
            password = kwargs.get('password')
            super(SingleRedisClient, self).__init__(
                host=host, port=port, password=password,
                max_connections=128, decode_responses=True
            )
        self.set_response_callback('GET', self._get)
        self.set_response_callback('HGETALL', self._hgetall)
        self.set_response_callback('HGET', self._hget)
        self.set_response_callback('HMGET', self._hmget)
        gevent.spawn(self._alive_check)
        gevent.sleep()

    # COMMAND EXECUTION AND PROTOCOL PARSING
    def execute_command(self, *args, **options):
        "Execute a command and return a parsed response"
        pool = self.connection_pool
        command_name = args[0]
        connection = pool.get_connection(command_name, **options)
        try:
            connection.send_command(*args)
            if command_name.upper() in ['HGETALL', 'HGET', 'HMGET', 'GET']:
                options['args'] = args
            return self.parse_response(connection, command_name, **options)
        except (ConnectionError, TimeoutError) as e:
            connection.disconnect()
            if not connection.retry_on_timeout and isinstance(e, TimeoutError):
                raise
            connection.send_command(*args)
            return self.parse_response(connection, command_name, **options)
        finally:
            pool.release(connection)

    @staticmethod
    def _get(response, **option):
        field = option.get('args')[1].split(':')[-1]
        if response is not None:
            field_prefix = field[:2]
            if field_prefix == 'i_':
                response = int(response)
            elif field_prefix == 'f_':
                response = float(response)
            elif field_prefix == 'b_':
                response = response not in ['0', 'False', 'false']
            elif field_prefix in ['d_', 'l_']:
                response = json.loads(response)
        return response

    @staticmethod
    def _hgetall(response, **option):
        response = pairs_to_dict(response)
        for k, v in response.items():
            if v is None:
                response[k] = v
                continue
            field_prefix = k[:2]
            if field_prefix == 'i_':
                response[k] = int(v)
            elif field_prefix == 'f_':
                response[k] = float(v)
            elif field_prefix == 'b_':
                response[k] = v not in ['0', 'False', 'false']
            elif field_prefix in ['d_', 'l_']:
                response[k] = json.loads(v)
        return response

    @staticmethod
    def _hget(response, **option):
        field = option.get('args')[2]
        if response is not None:
            field_prefix = field[:2]
            if field_prefix == 'i_':
                response = int(response)
            elif field_prefix == 'f_':
                response = float(response)
            elif field_prefix == 'b_':
                response = response not in ['0', 'False', 'false']
            elif field_prefix in ['d_', 'l_']:
                response = json.loads(response)
        return response

    @staticmethod
    def _hmget(response, **option):
        _response = {}
        fields = option.get('args')[2:]
        for field, value in zip(fields, response):
            if value is None:
                _response[field] = value
                continue
            field_prefix = field[:2]
            if field_prefix == 'i_':
                _response[field] = int(value)
            elif field_prefix == 'f_':
                _response[field] = float(value)
            elif field_prefix == 'b_':
                _response[field] = value not in ['0', 'False', 'false']
            elif field_prefix in ['d_', 'l_']:
                _response[field] = json.loads(value)
            else:
                _response[field] = value
        return _response

    def _alive_check(self):
        """
        Redis 存活检测
        """
        while True:
            try:
                if self.ping():
                    self.status.alive_timestamp = int(time.time())
            except Exception as e:
                log.exception(e)
                log.error('Redis Connection Exception.')
            gevent.sleep(3)

    def get_connection_status(self):
        return self.status

    def robust(self, func, *args, **kwargs):
        """
        对命令进行bobust的封装
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return func(*args, **kwargs)
        except ResponseError as e:
            log.exception(e)
            log.debug(e)
            return None
        except Exception as e:
            log.exception(e)
            log.debug('Try Again.')
            if self.connection_pool._created_connections != 0:
                self.connection_pool.reset()
            gevent.sleep(2)
            return self.robust(func, *args, **kwargs)

    def setex(self, name, time, value):
        return super(SingleRedisClient, self).setex(name, value, time)

    def smadd(self, name, values):
        '''
        批量sadd
        '''
        with self.pipeline() as ppl:
            for value in values:
                ppl.sadd(name, value)
            ppl.execute()

    def smpop(self, name, count):
        '''
        批量spop
        '''
        with self.pipeline() as ppl:
            for _ in range(count):
                ppl.spop(name)
            ppl.execute()

    def hmdel(self, name, values):
        '''
        批量hdel
        '''
        with self.pipeline() as ppl:
            for value in values:
                ppl.hdel(name, value)
            ppl.execute()

    def hmove(self, old_name, new_name, key, value):
        with self.pipeline() as ppl:
            if old_name:
                ppl.hdel(old_name, key)
            ppl.hset(new_name, key, value)
            ppl.execute()

    def psubscribe(self, pattern):
        '''
        匹配订阅
        '''
        ps = self.pubsub()
        ps.psubscribe(pattern)
        log.info('Subscribe %s...' % pattern)
        for item in ps.listen():
            yield item
        ps.unsubscribe('spub')
        log.warning('Subscribe Was Exit.')

    def set_the_hash_value_for_the_hash(self, name, key, value_name, value_key, value):
        with self.pipeline() as ppl:
            ppl.hset(value_name, value_key, value)
            ppl.hset(name, key, value_name)
            ppl.execute()

    def get_the_hash_value_for_the_hash(self, name, key, value_key=None):
        value_name = self.hget(name, key)
        value = self.hget(value_name, value_key) if value_key else self.hgetall(value_name)
        return value

    def clean(self, pattern='*'):
        def _clean(_pattern):
            keys = self.keys(pattern)
            if not keys:
                return True
            self.delete(*keys)
            return True
        return self.robust(_clean, pattern)
    
    def hmgetall(self, *names):
        def _hmgetall(*_names):
            with self.pipeline(transaction=False) as ppl:
                for name in _names:
                    ppl.hgetall(name)
                ret = ppl.execute()
            return ret
        return self.robust(_hmgetall, *names)

    def hmget_all(self, names, field='all'):
        def _hmget_all(_names, _field):
            with self.pipeline(transaction=False) as ppl:
                for name in _names:
                    ppl.hget(name, _field)
                ret = ppl.execute()
            return ret
        return self.robust(_hmget_all, names, field)

    @staticmethod
    def timer(seconds, callback, *args, **kwargs):
        def _timer(_callback, *_args, **_kwargs):
            callback(*_args, **_kwargs)

        gevent.spawn_later(seconds, _timer, callback, *args, **kwargs)
        gevent.sleep()


RedisClient = SingleRedisClient
