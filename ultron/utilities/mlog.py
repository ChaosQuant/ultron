# -*- coding: utf-8 -*-

import threading
import logging
import datetime
import sys
import os

class Singleton(object):
    objs = {}
    objs_locker = threading.Lock()

    def __new__(cls, *args, **kv):
        if cls in cls.objs:
            return cls.objs[cls]['obj']

        cls.objs_locker.acquire()
        try:
            if cls in cls.objs:
                return cls.objs[cls]['obj']
            obj = object.__new__(cls)
            cls.objs[cls] = {'obj':obj, 'init':False}
            setattr(cls, '__init__', cls.decorate_init(cls.__init__))
            return cls.objs[cls]['obj']
        finally:
            cls.objs_locker.release()

    @classmethod
    def decorate_init(cls, fn):
        def init_wrap(*args):
            if not cls.objs[cls]['init']:
                fn(*args)
                cls.objs[cls]['init'] = True
            return
        return init_wrap

class MLog(Singleton):
    
    def __init__(self):
        self.config(level=logging.DEBUG)
        
    def config(self, name="logging", level=logging.DEBUG):
        """
        Constructor
        """
        dir_name = os.path.expandvars('$HOME') + '/MLOG/' + name + '/'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        filename = dir_name + name + '_' + datetime.datetime.now().strftime('%b_%d_%H_%M')+'.log'
        format_str = "[%(process)d %(thread)d][%(asctime)s][%(filename)s line:%(lineno)d][%(levelname)s] %(message)s"
        # define a Handler which writes INFO messages or higher to the sys.stderr
        logging.basicConfig(level=level,
                            format=format_str,
                            datefmt='%m-%d %H:%M',
                            filename=filename,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter(format_str)
        console.setFormatter(formatter)
        # 将定义好的console日志handler添加到root logger
        logging.getLogger('').addHandler(console)


    @classmethod
    def write(self):
        return logging
