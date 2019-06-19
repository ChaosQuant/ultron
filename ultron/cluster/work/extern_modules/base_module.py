# -*- coding: utf-8 -*-

class BaseModule(object):
    def __init__(self, name, wid, token, redis_client):
        __str__ = name
        self._redis_client = redis_client
        self._wid = wid
        self._token = token