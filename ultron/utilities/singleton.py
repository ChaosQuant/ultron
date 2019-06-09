# -*- coding: utf-8 -*-

from collections import defaultdict
class Singleton(type):
    """
    单例metaclass
    """

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = defaultdict()

    def __call__(cls, *args, **kw):
        tag = kw.get('tag') or 'default'
        if cls._instance.get(tag) is None:
            cls._instance[tag] = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance[tag]