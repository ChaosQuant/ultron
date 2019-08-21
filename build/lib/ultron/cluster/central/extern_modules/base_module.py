# -*- coding: utf-8 -*-

class BaseModule(object):
    def __init__(self, name, redis_client):
        __str__ = name
        self._redis_client = redis_client